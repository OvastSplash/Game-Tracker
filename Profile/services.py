from RAWGapi.models import Game as GameModel, UserGame
from GameTracker.settings import RAWG_API_TOKEN
from RAWGapi.serializers import GameListSerializer
import requests


class GameService:  
    """Сервис для работы с играми"""
    
    @staticmethod
    def get_game_from_db(game_slug):
        """
        Получает игру из базы данных со всеми связанными объектами
        
        Args:
            game_slug (str): Слаг игры
            
        Returns:
            GameModel или None: Объект игры или None если не найдена
        """
        try:
            return GameModel.objects.prefetch_related(
                'genres', 
                'platforms', 
                'stores', 
                'developers'
            ).get(slug=game_slug)
        except GameModel.DoesNotExist:
            return None
    
    @staticmethod
    def create_game_via_api(game_slug, access_token, request):
        """
        Создает игру через внутренний API
        
        Args:
            game_slug (str): Слаг игры
            access_token (str): JWT токен
            request: HTTP запрос для построения URL
            
        Returns:
            tuple: (GameModel или None, ошибка или None)
        """
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
            game = GameService.get_game_from_db(game_slug)
            return game, None
            
        except requests.RequestException as e:
            return None, f'Ошибка при запросе к API: {str(e)}'
    
    @staticmethod
    def get_or_create_game(game_slug, access_token, request):
        """
        Получает игру из БД или создает через API
        
        Args:
            game_slug (str): Слаг игры
            access_token (str): JWT токен
            request: HTTP запрос
            
        Returns:
            tuple: (GameModel или None, ошибка или None)
        """
        # Сначала пытаемся найти в базе
        game = GameService.get_game_from_db(game_slug)
        if game:
            return game, None
        
        # Если не найдено, создаем через API
        game, error = GameService.create_game_via_api(game_slug, access_token, request)
        if error:
            return None, error
        
        if not game:
            return None, 'Игра не была создана через API'
        
        return game, None
    
    @staticmethod
    def serialize_game_data(game):
        """
        Преобразует объект игры в словарь для шаблона
        
        Args:
            game (GameModel): Объект игры с предзагруженными связями
            
        Returns:
            dict: Словарь с данными игры
        """
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


class UserGameService:
    """Сервис для работы с играми пользователя"""
    
    @staticmethod
    def get_user_game(user, game_slug):
        """
        Проверяет, есть ли игра в коллекции пользователя
        
        Args:
            user: Объект пользователя
            game_slug (str): Слаг игры
            
        Returns:
            UserGame или None: Объект связи пользователь-игра или None
        """
        try:
            return UserGame.objects.get(user=user, game__slug=game_slug)
        except UserGame.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_games_with_prefetch(user_id):
        """
        Получает все игры пользователя с предзагруженными связями
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            QuerySet: Запрос с играми пользователя
        """
        return UserGame.objects.filter(user=user_id).prefetch_related(
            'game',
            'game__genres',
            'game__platforms',
            'game__stores',
            'game__developers',
        )


class AuthService:
    """Сервис для работы с авторизацией"""
    
    @staticmethod
    def get_access_token(request):
        if 'tokens' in request.session:
            return request.session['tokens'].get('access')
        return None 
    
class DeveloperService:
    """Сервис для работы с разработчиками"""
    
    @staticmethod
    def get_developer_id(developer_name):
        """
        Получает ID разработчика
        
        Args:
            developer_name (str): Название разработчика
            
        Returns:
            tuple: (ID разработчика, success: bool)
        """
        params = {
            'key': RAWG_API_TOKEN,
            'search': developer_name,
        }
        
        response = requests.get("https://api.rawg.io/api/developers", params=params)
        
        if response.status_code == 200:
            data = response.json()
            developer_id = data.get('results')[0].get('id')
            return developer_id, True
        
        return None, False
    
    @staticmethod
    def get_developer_games(developer_id):
        params = {
            'key': RAWG_API_TOKEN,
            'developers': developer_id,
            'exclude_additions': True
        }
        
        response = requests.get("https://api.rawg.io/api/games", params=params)
        data = response.json()
        developer_games = data.get('results')
        
        unwanted_keywords = [
            'companion', 'launcher', 'soundtrack', 'demo',
            'pack', 'dlc', 'tool', 'editor', 'test', 'benchmark',
            'trailer', 'mod', 'server', 'redeem', 'expansion', "collection",
        ]
        
        sorted_developer_games = [game for game in developer_games if not any(keyword in game['name'].lower() or keyword in game['slug'].lower() for keyword in unwanted_keywords)]
        sorted_developer_games = sorted(sorted_developer_games, key=lambda game: game.get('metacritic', 0) or 0, reverse=True)
        serializer = GameListSerializer(data=sorted_developer_games, many=True)
        
        if serializer.is_valid():
            return serializer.data, True
        
        return [], False