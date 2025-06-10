from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import get_object_or_404
from RAWGapi.models import UserGame
from RAWGapi.object_to_json_serializers import UserGameSerializer
from django.db.models import Count, Q
from .services import GameService, UserGameService, AuthService, DeveloperService
from SteamAPI.services import SteamService
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
        
        # Получаем игры из Steam
        if hasattr(user, 'steam_id') and user.steam_id:
            if len(str(user.steam_id)) != 17:
                steam_id, success = SteamService.resolve_and_update_steam_id(user, user.steam_id)
            else:
                success = True
                
            if success:
                user_games = set(UserGame.objects.filter(user=user).values_list('game__name', flat=True))
                steam_games, get_steam_games_success = SteamService.get_user_steam_games(user, user_games)
                print(f"Steam ID обновлен: {user.steam_id}")
                if get_steam_games_success:
                    game_playtimes, total_hours = SteamService.get_user_playtime(user_games, steam_games)
                    total_hours = f"{total_hours} ч."
                    print(f"Игровое время было успешно получено {game_playtimes} и общее время {total_hours}")
                else:
                    print(f"Не удалось получить игры из Steam: {user.steam_id}")
            else:
                print(f"Steam ID не обновлен: {user.steam_id}")
            
        user_id = user.id
        
        # Получаем игры пользователя через сервис
        games = UserGameService.get_user_games_with_prefetch(user_id)
        games_serialized = UserGameSerializer(games, many=True).data
        
        # Получаем access токен через сервис
        access_token = AuthService.get_access_token(request)
        
        user_stats = UserGame.objects.filter(user=user).aggregate(
            total_games=Count('id'),
            games_ended=Count('id', filter=Q(status='COMPLETED')),
            games_in_progress=Count('id', filter=Q(status='PLAYING')),
            games_not_started=Count('id', filter=Q(status='PLAN_TO_PLAY')),
        )
        
        return render(request, 'profile/profile.html', {
            'user': request.user, 
            'user_games_json': json.dumps(games_serialized, ensure_ascii=False),
            'game_playtimes_json': json.dumps(game_playtimes, ensure_ascii=False),
            'access_token': access_token,
            'games_count': user_stats['total_games'],
            'games_ended': user_stats['games_ended'],
            'games_in_progress': user_stats['games_in_progress'],
            'games_not_started': user_stats['games_not_started'],
            'total_hours': total_hours
        })

@method_decorator(login_required, name="dispatch")        
class Game(View):
    """Представление для работы с отдельной игрой"""
    
    def get(self, request, GameSlug):
        """
        Отображает детальную информацию об игре
        Получает данные из БД или создает через API
        """
        # Получаем токен авторизации
        access_token = AuthService.get_access_token(request)
        
        # Получаем или создаем игру
        game, error = GameService.get_or_create_game(GameSlug, access_token, request)
        if error:
            return self._render_error(error, GameSlug)
        
        # Проверяем, есть ли игра в коллекции пользователя
        user_game = UserGameService.get_user_game(request.user, GameSlug)
        
        # Преобразуем игру в словарь для шаблона
        game_data = GameService.serialize_game_data(game)
        
        return render(request, 'profile/game.html', {
            'game': game_data,
            'user_game': user_game,
            'access_token': access_token,
            'back_url': '/profile/'
        })
    
    def post(self, request, GameSlug):
        """Удаление игры из коллекции пользователя"""
        user_game = get_object_or_404(
            UserGame.objects.filter(user=request.user).select_related('game'), 
            game__slug=GameSlug
        )
        user_game.delete()
    
    def _render_error(self, error_message, game_slug, request):
        """Отображает страницу с ошибкой"""
        return render(request, 'profile/game_error.html', {
            'error': error_message,
            'game_slug': game_slug
        })
        
# Показывает игры разработчика
@method_decorator(login_required, name="dispatch")
class Developer(View):
    def get(self, request, developer_name):
        developer_id, developer_id_success = DeveloperService.get_developer_id(developer_name)
        
        if developer_id_success:
            developer_games, developer_games_success = DeveloperService.get_developer_games(developer_id)
            
            if developer_games_success:
                # Определяем предыдущую страницу для кнопки "Назад"
                referer = request.META.get('HTTP_REFERER', '')
                back_url = '/profile/'  # По умолчанию на профиль
                
                # Если пришли с игры или профиля
                if '/profile/' in referer:
                    back_url = referer
                
                return render(request, 'profile/developer.html', {
                    'developer_games': developer_games,
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