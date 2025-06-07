from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import get_object_or_404
from RAWGapi.models import Game as GameModel, UserGame
import json
import requests
from django.conf import settings

from RAWGapi.models import UserGame
from RAWGapi.object_to_json_serializers import UserGameSerializer
# Create your views here.

@method_decorator(login_required, name='dispatch')
class Profile(View):
    def get(self, request):
        user_id = request.user.id
        games = UserGame.objects.filter(user=user_id)
        # Сериализуем игры пользователя для передачи в шаблон
        games_serialized = UserGameSerializer(games, many=True).data
        print(games_serialized)
        
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
            'access_token': access_token,
            'games_count': games_count,
            'games_ended': games_ended,
            'games_in_progress': games_in_progress,
            'games_not_started': games_not_started
        })

@method_decorator(login_required, name="dispatch")        
class Game(View):
    def get(self, request, GameSlug):
        """
        Представление для отображения детальной информации об игре
        Получает данные через внутренний API и показывает их пользователю
        """
        # Получаем access токен для JavaScript и API запросов
        access_token = None
        if 'tokens' in request.session:
            access_token = request.session['tokens'].get('access')
        
        # Попробуем найти игру в нашей базе данных
        try:
            game = GameModel.objects.get(slug=GameSlug)
            game_data = {
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
        except GameModel.DoesNotExist:
            # Если игры нет в базе, получаем данные через наш внутренний API
            if not access_token:
                return render(request, 'profile/game_error.html', {
                    'error': 'Отсутствует токен авторизации',
                    'game_slug': GameSlug
                })
            
            # Делаем POST запрос к нашему API с addGame: false
            api_url = request.build_absolute_uri(f"/api/game/{GameSlug}/")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.post(api_url, 
                                       headers=headers, 
                                       json={'addGame': False})
                
                if response.status_code in [200, 201]:
                    api_data = response.json()
                    if api_data.get('status') == 'success':
                        # Теперь получаем игру из базы (она должна была создаться)
                        try:
                            game = GameModel.objects.get(slug=GameSlug)
                            game_data = {
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
                        except GameModel.DoesNotExist:
                            return render(request, 'profile/game_error.html', {
                                'error': 'Игра не была создана через API',
                                'game_slug': GameSlug
                            })
                    else:
                        return render(request, 'profile/game_error.html', {
                            'error': f"Ошибка API: {api_data.get('message', 'Неизвестная ошибка')}",
                            'game_slug': GameSlug
                        })
                else:
                    return render(request, 'profile/game_error.html', {
                        'error': f'API вернул код {response.status_code}',
                        'game_slug': GameSlug
                    })
            except requests.RequestException as e:
                return render(request, 'profile/game_error.html', {
                    'error': f'Ошибка при запросе к API: {str(e)}',
                    'game_slug': GameSlug
                })
        
        # Проверяем, есть ли игра в коллекции пользователя
        user_game = None
        if hasattr(game_data, 'slug'):
            try:
                user_game = UserGame.objects.get(user=request.user, game__slug=game_data.slug)
            except UserGame.DoesNotExist:
                pass
        elif 'slug' in game_data:
            try:
                user_game = UserGame.objects.get(user=request.user, game__slug=game_data['slug'])
            except UserGame.DoesNotExist:
                pass
        
        return render(request, 'profile/game.html', {
            'game': game_data,
            'user_game': user_game,
            'access_token': access_token
        })
        
    def post(self, request, GameSlug):
        access_token = None
        if 'tokens' in request.session:
            access_token = request.session['tokens'].get('access')
            
        game = get_object_or_404(UserGame.objects.filter(user=request.user).prefetch_related('game'), game__slug=GameSlug)
        game.delete()