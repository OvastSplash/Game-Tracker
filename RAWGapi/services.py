from GameTracker.settings import RAWG_API_TOKEN
from RAWGapi.models import UserGame, Game, Genre
from django.db.models import Count
from RAWGapi.models import UserGame
import requests

class RawgApiService:
    @staticmethod
    def get_detailed_game_data(game_slug):
        """
        Получает детальную информацию об игре из RAWG API
        Args:
            game_slug: Slug игры
            
        Returns:
            tuple: (data: dict, success: bool)
        """
        params = {
            'key': RAWG_API_TOKEN,
        }
        url = f"https://api.rawg.io/api/games/{game_slug}/"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json(), True
        else:
            return None, False
        
    @staticmethod
    def search_games(game_name):
        """
        Ищет игры по названию
        Args:
            game_name: Название игры
            
        Returns:
            tuple: (games: list, success: bool)
        """
        params = {
            'key': RAWG_API_TOKEN,
            'search': game_name,
            'page_size': 10,  # Увеличиваем количество для лучшей фильтрации
            'ordering': '-metacritic,-rating,-added',  # Приоритет Metacritic рейтингу
            
            # === ФИЛЬТРЫ КАЧЕСТВА ===
            # 'metacritic': '65,100',        # Только игры с Metacritic 65+
            # 'rating': '3.5,5',             # Только игры с рейтингом 3.5+
            # 'reviews_count': '50,999999',   # Минимум 50 отзывов
            
            # === ФИЛЬТРЫ ПЛАТФОРМ (исключаем мобильные) ===
            'platforms': '4,187,1,18,186,7', # PC, PS5, Xbox One, PS4, Xbox Series, Nintendo Switch
            
            # === ВРЕМЕННЫЕ ФИЛЬТРЫ ===
            # 'dates': '2000-01-01', # Игры с 2010
        }
        
        url = "https://api.rawg.io/api/games"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', []), True
        else:
            return None, False

class GameStatusValidation:
    VALID_STATUSES = [choice[0] for choice in UserGame.STATUS_CHOICES]
    
    @classmethod
    def validate_status(cls, status):
        """
        Проверяет, является ли статус допустимым
        Args:
            status: Статус игры
            
        Returns:
            tuple: (success: bool, message: str)
        """
        
        if status in cls.VALID_STATUSES:
            return True, None
        
        return False, "Неверный статус"

class GameManagementService:
    @staticmethod
    def get_game_by_slug(game_slug):
        """
        Получает игру по slug
        Args:
            game_slug: Slug игры
            
        Returns:
            Game: Игра
        """
        try:
            return Game.objects.get(slug=game_slug)
        except Game.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_game_by_slug(user, game_slug):
        """
        Получает игру по slug
        Args:
            user: Пользователь
            game_slug: Slug игры
            
        Returns:
            UserGame: Игры пользователя
        """
        try:
            return UserGame.objects.filter(user=user).prefetch_related('game').get(game__slug=game_slug)
        except UserGame.DoesNotExist:
            return None
    
    @staticmethod
    def add_game_to_user_collection(user, game):
        """
        Добавляет игру в коллекцию пользователя
        Args:
            user: Пользователь
            game: Игра
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if UserGame.objects.filter(user=user, game=game).exists():
            return False, "Игра уже в коллекции"
        
        UserGame.objects.create(user=user, game=game)
        return True, "Игра успешно добавлена в коллекцию"
    
    @staticmethod
    def remove_game_from_user_collection(user, game_slug):
        try:
            game = UserGame.objects.filter(user=user).prefetch_related('game').get(game__slug=game_slug)
            game.delete()
            return True, "Игра успешно удалена из коллекции"
        except UserGame.DoesNotExist:
            return False, "Игра не найдена"
    
    @staticmethod
    def add_game_to_database(game_slug):
        """
        Добавляет игру в базу данных
        Args:
            game_name: Название игры
            
        Returns:
            tuple: (game: Game, success: bool, game_exists: bool)
        """
        
        try:
            game = Game.objects.get(slug=game_slug)
            return game, True, True
        except Game.DoesNotExist:
            pass
        
        params = {
            'key': RAWG_API_TOKEN,
        }
        url = f"https://api.rawg.io/api/games/{game_slug}"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            game_data = response.json()
            return game_data, True, False
        
        return None, False, False
    
    @staticmethod
    def update_game_status(user, game_slug, status):
        """
        Обновляет статус игры
        Args:
            user: Пользователь
            game_slug: Slug игры
            status: Новый статус
            
        Returns:
            tuple: (success: bool, message: str)
        """
        
        is_valid = GameStatusValidation.validate_status(status)
        if is_valid:
            try:
                game = UserGame.objects.filter(user=user).prefetch_related('game').get(game__slug=game_slug)
                game.status = status
                game.save()
            except UserGame.DoesNotExist:
                return False, "Игра не найдена"
            
            return True, "Статус игры успешно обновлен"
        else:
            return False, "Неверный статус"
        
    @staticmethod
    def update_game_raiting(user, game_slug, raiting):
        """
        Обновляет рейтинг игры
        Args:
            user: Пользователь
            game: Игра
            raiting: Новый рейтинг
            
        Returns:
            tuple: (success: bool, message: str)
        """
        
        try:
            game = UserGame.objects.filter(user=user).prefetch_related('game').get(game__slug=game_slug)
            game.user_raiting = raiting
            game.save()
            return True, "Рейтинг игры успешно обновлен"
        except UserGame.DoesNotExist:
            return False, "Игра не найдена"
        
    @staticmethod
    def get_user_games(user):
        """
        Получает все игры пользователя
        Args:
            user: Пользователь
            
        Returns:
            list: Игры пользователя
        """
        try:
            user_games = UserGame.objects.filter(user=user).prefetch_related('game')
            return user_games
        except UserGame.DoesNotExist:
            return None

class RecomendedGamesService:
    @staticmethod
    def get_favorite_genres(user, limit_genres=5):
        """
        Получает любимые жанры пользователя
        Args:
            user: Пользователь
            limit_genres: Максимальное количество жанров
            
        Returns:
            list: Жанры пользователя
        """
        user_game_slugs = Genre.objects.filter(games__usergame__user=user).annotate(
            count=Count('games__usergame', distinct=True)
        ).order_by('-count')[:limit_genres]
        
        if len(user_game_slugs):
            return user_game_slugs
        else:
            return None
    
    @staticmethod
    def get_recomended_games(user, top_genres):
        """
        Получает рекомендованные игры
        Args:
            user: Пользователь
            top_genres: Жанры пользователя
            
        Returns:
            list: Игры пользователя
        """
        
        params = {
            'key': RAWG_API_TOKEN,
            'page_size': UserGame.objects.filter(user=user).count() + 10,
            'metacritic': '75,100',
            'ordering': '-metacritic,-rating,-added',
        }
        if top_genres:
            genres_string = ",".join([genre.name.lower().replace(" ", "-") for genre in top_genres[:len(top_genres)]])
            params['genres'] = genres_string
            
        response = requests.get("https://api.rawg.io/api/games", params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        
        else:
            return None
        
    @staticmethod
    def filter_games(games, user_game_slugs):
        """
        Фильтрует игры
        Args:
            games: Игры
            user_game_slugs: Slug игр пользователя
            
        Returns:
            list: Игры пользователя
        """
        
        filtered_games = []
        for game in games:
            if game['slug'] not in user_game_slugs:
                filtered_games.append(game)
                
        return filtered_games