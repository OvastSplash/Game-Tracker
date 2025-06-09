from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import get_object_or_404
from RAWGapi.models import Game as GameModel, UserGame
from RAWGapi.serializers import GameListSerializer
from SteamAPI.views import AuthSteamID
from RAWGapi.models import UserGame
from RAWGapi.object_to_json_serializers import UserGameSerializer
from GameTracker.settings import STEAM_API_TOKEN, RAWG_API_TOKEN
import json
import requests
# Create your views here.

@method_decorator(login_required, name='dispatch')
class Profile(View):
    def get(self, request):
        # Проверяем, есть ли Steam ID у пользователя
        user = request.user
        game_playtimes = {}
        total_hours = "—"
        
        if hasattr(user, 'steam_id') and user.steam_id:
            if len(str(user.steam_id)) != 17:
                response = AuthSteamID.get(self, request, user.steam_id)
                if response.status_code == 200:
                    user.steam_id = response.data['response']['steamid']
                    user.save()
                    print(f"Steam ID обновлен: {user.steam_id}")
                    
            if len(str(user.steam_id)) == 17:
                game_playtimes, total_hours_int = self.get_user_games(user)
                total_hours = f"{total_hours_int} ч."
            
        user_id = user.id
        games = UserGame.objects.filter(user=user_id)
        # Сериализуем игры пользователя для передачи в шаблон
        games_serialized = UserGameSerializer(games, many=True).data
        
        # Получаем access токен из session для передачи в JavaScript
        access_token = None
        if 'tokens' in request.session:
            access_token = request.session['tokens'].get('access')
            
        games_count = UserGame.objects.filter(user=user_id).count()
        games_ended = UserGame.objects.filter(user=user_id, status='COMPLETED').count()
        games_in_progress = UserGame.objects.filter(user=user_id, status='PLAYING').count()
        games_not_started = UserGame.objects.filter(user=user_id, status='PLAN_TO_PLAY').count()
        
        return render(request, 'profile/profile.html', {
            'user': request.user, 
            'user_games_json': json.dumps(games_serialized, ensure_ascii=False),
            'game_playtimes_json': json.dumps(game_playtimes, ensure_ascii=False),
            'access_token': access_token,
            'games_count': games_count,
            'games_ended': games_ended,
            'games_in_progress': games_in_progress,
            'games_not_started': games_not_started,
            'total_hours': total_hours
        })
        
    def get_user_games(self, user):
        userGames = set(UserGame.objects.filter(user=user).prefetch_related('game').values_list('game__name', flat=True))
        steamGames = self.get_user_steam_games(user)
        sortedGames = {}
        hours_total = 0
        
        if steamGames and 'response' in steamGames and 'games' in steamGames['response']:
            for game in steamGames['response']['games']:
                name = game['name']
                if name.lower() in (value.lower() for value in userGames):
                    time_in_minutes = game['playtime_forever']
                    hours_decimal = round(time_in_minutes / 60, 1)
                    hours_total += hours_decimal
                    formatted_time = f"{hours_decimal} ч."
                    sortedGames[name] = formatted_time
            
            print(int(hours_total))
            print(sortedGames)
            return sortedGames, int(hours_total)
        
        return sortedGames, 0

    def get_user_steam_games(self, user):
        try:
            params = {
                'key': STEAM_API_TOKEN,
                'steamid': user.steam_id,
                'format': 'json',
                'include_appinfo': 1,
                'include_played_free_games': 1,
            }
            response = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', params=params)
            
            if response.status_code == 200:
                if response.text.strip():
                    return response.json()
                else:
                    print("Steam API вернул пустой ответ")
                    return None
            else:
                print(f"Steam API вернул код {response.status_code}: {response.text}")
                return None
                
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Ошибка при запросе к Steam API: {e}")
            return None

@method_decorator(login_required, name="dispatch")        
class Game(View):
    def get(self, request, GameSlug):
        """
        Представление для отображения детальной информации об игре
        Получает данные через внутренний API и показывает их пользователю
        """
        # Проверяем токен авторизации
        access_token = self._get_access_token(request)
        
        # Пытаемся получить игру из базы или создать через API
        game_data, error = self._get_or_create_game_data(GameSlug, access_token, request)
        if error:
            return self._render_error(error, GameSlug, request)
        
        # Проверяем, есть ли игра в коллекции пользователя
        user_game = self._check_user_game(request.user, game_data)
        
        # Для страницы игры всегда возвращаемся на профиль
        back_url = '/profile/'
        
        return render(request, 'profile/game.html', {
            'game': game_data,
            'user_game': user_game,
            'access_token': access_token,
            'back_url': back_url
        })
    
    def _get_access_token(self, request):
        """Получает access токен из сессии"""
        if 'tokens' in request.session:
            return request.session['tokens'].get('access')
        return None
    
    def _create_game_data_dict(self, game):
        """Создает словарь с данными игры из объекта модели"""
        return {
            'name': game.name,
            'slug': game.slug,
            'description': game.description,
            'background_image': game.logo,
            'released': game.release_date,
            'metacritic': game.metacritic,
            'genres': [{'name': genre.name} for genre in game.genres.all()],
            'platforms': [{'platform': {'name': platform.name}} for platform in game.platforms.all()],
            'stores': [{'name': store.name} for store in game.stores.all()],
            'developers': [{'name': developer.name} for developer in game.developers.all()],
        }
    
    def _get_game_from_db(self, game_slug):
        """Пытается найти игру в базе данных"""
        try:
            game = GameModel.objects.get(slug=game_slug)
            return self._create_game_data_dict(game), None
        except GameModel.DoesNotExist:
            return None, None
    
    def _create_game_via_api(self, game_slug, access_token, request):
        """Создает игру через API и возвращает данные"""
        if not access_token:
            return None, 'Отсутствует токен авторизации'
        
        api_url = request.build_absolute_uri(f"/api/game/{game_slug}/")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(api_url, headers=headers, json={'addGame': False})
            
            if response.status_code not in [200, 201]:
                return None, f'API вернул код {response.status_code}'
            
            api_data = response.json()
            if api_data.get('status') != 'success':
                return None, f"Ошибка API: {api_data.get('message', 'Неизвестная ошибка')}"
            
            # Получаем созданную игру из базы
            return self._get_game_from_db(game_slug)
            
        except requests.RequestException as e:
            return None, f'Ошибка при запросе к API: {str(e)}'
    
    def _get_or_create_game_data(self, game_slug, access_token, request):
        """Получает данные игры из базы или создает через API"""
        # Сначала пытаемся найти в базе
        game_data, error = self._get_game_from_db(game_slug)
        if game_data:
            return game_data, None
        
        # Если не найдено, создаем через API
        game_data, error = self._create_game_via_api(game_slug, access_token, request)
        if error:
            return None, error
        
        if not game_data:
            return None, 'Игра не была создана через API'
        
        return game_data, None
    
    def _check_user_game(self, user, game_data):
        """Проверяет, есть ли игра в коллекции пользователя"""
        # Получаем slug из данных игры
        if isinstance(game_data, dict):
            slug = game_data.get('slug')
        else:
            slug = getattr(game_data, 'slug', None)
        
        if not slug:
            return None
        
        try:
            return UserGame.objects.get(user=user, game__slug=slug)
        except UserGame.DoesNotExist:
            return None
    
    def _render_error(self, error_message, game_slug, request):
        """Отображает страницу с ошибкой"""
        return render(request, 'profile/game_error.html', {
            'error': error_message,
            'game_slug': game_slug
        })
    
    # Удаление игры из коллекции 
    def post(self, request, GameSlug):
        game = get_object_or_404(UserGame.objects.filter(user=request.user).prefetch_related('game'), game__slug=GameSlug)
        game.delete()
        
# Показывает игры разработчика
@method_decorator(login_required, name="dispatch")
class Developer(View):
    def get(self, request, developer_name):
        developer_id_params = {
            'key': RAWG_API_TOKEN,
            'search': developer_name,
        }
        developer_id_response = requests.get("https://api.rawg.io/api/developers", params=developer_id_params)
        developer_id = developer_id_response.json().get('results')[0].get('id')
        
        if developer_id:
            developer_games_params = {
                'key': RAWG_API_TOKEN,
                'developers': developer_id,
                'exclude_additions': True,
            }
            developer_games_response = requests.get("https://api.rawg.io/api/games", params=developer_games_params)
            developer_games = developer_games_response.json().get('results')
            
            unwanted_keywords = [
                'companion', 'launcher', 'soundtrack', 'demo',
                'pack', 'dlc', 'tool', 'editor', 'test', 'benchmark',
                'trailer', 'mod', 'server', 'redeem', 'expansion', "collection",
            ]
            sorted_developer_games = [game for game in developer_games if not any(keyword in game['name'].lower() or keyword in game['slug'].lower() for keyword in unwanted_keywords)]
            
            sorted_developer_games = sorted(sorted_developer_games, key=lambda game: game.get('metacritic', 0) or 0, reverse=True)
            serializer = GameListSerializer(data=sorted_developer_games, many=True)
            
            if serializer.is_valid():
                # Определяем предыдущую страницу для кнопки "Назад"
                referer = request.META.get('HTTP_REFERER', '')
                back_url = '/profile/'  # По умолчанию на профиль
                
                # Если пришли с игры или профиля
                if '/profile/' in referer:
                    back_url = referer
                
                return render(request, 'profile/developer.html', {
                    'developer_games': serializer.data,
                    'developer_name': developer_name,
                    'back_url': back_url
                })
            
        # Определяем предыдущую страницу для кнопки "Назад"
        referer = request.META.get('HTTP_REFERER', '')
        back_url = '/profile/'  # По умолчанию на профиль
        
        # Если пришли с игры или профиля
        if '/profile/' in referer:
            back_url = referer
            
        return render(request, 'profile/developer_error.html', {
            'developer_name': developer_name,
            'back_url': back_url
        })