from rest_framework.views import APIView
from rest_framework.response import Response
from .object_to_json_serializers import UserGameSerializer
from .serializers import GameListSerializer
from .create_serializers import GameSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .services import GameManagementService, RecomendedGamesService, RawgApiService
from .models import UserGame
import time
User = get_user_model()

class GameList(APIView):
    """
    Класс для поиска игр через RAWG API
    GET запрос возвращает топ-5 игр, отсортированных по рейтингу Metacritic
    """
    def get(self, request, GameName):
        # Формируем URL для поиска игр, ограничиваем 5 результатами

        games, success = RawgApiService.search_games(GameName)
        
        if success:
            # Сортируем игры по рейтингу Metacritic (если нет рейтинга, считаем его за 0)
            sorted_games = sorted(games, key=lambda x: x.get('metacritic', 0) or 0, reverse=True)
            
            serializer = GameListSerializer(data=sorted_games, many=True)
            if serializer.is_valid():
                return Response(serializer.data)
        
        return Response(serializer.errors, status=400)
    
class GetGame(APIView):
    """
    Класс для работы с конкретной игрой
    Требует аутентификации через JWT
    GET: получение информации об игре
    POST: добавление игры в коллекцию пользователя
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, GameName):
        """Получение детальной информации об игре из RAWG API"""
        print(GameName)
        data, success = RawgApiService.get_detailed_game_data(GameName)
        print(data)
        if success:
            print("success")
            serializer = GameListSerializer(data=data)
            if serializer.is_valid():
                print("valid")
                return Response(serializer.data)
            return Response(status=400)
        else:
            return Response(status=404)
        
    def post(self, request, GameName):
        """
        Добавление игры в коллекцию пользователя
        1. Проверяет, существует ли игра в базе
        2. Если игра существует:
           - проверяет, нет ли её уже в коллекции пользователя
           - если нет, добавляет связь пользователь-игра
        3. Если игры нет:
           - получает данные из RAWG API
           - создает новую игру
           - добавляет связь пользователь-игра
        """
        user = request.user
        
        game_data, game_created_success, game_exists = GameManagementService.add_game_to_database(GameName)
        
        if not game_created_success:
            return Response({
                "status": "error",
                "message": "Failed to get game data",
                "code": "api_error"
            }, status=400)
        
        if game_exists:
            game = game_data
        else:
            serializer = GameSerializer(data=game_data)
            if serializer.is_valid():
                game = serializer.save()
                print(f"Created new game: {game.name}")
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid game data",
                    "code": "validation_error",
                    "errors": serializer.errors
                }, status=400)
        
        addGame = request.data.get('addGame', True)
        if addGame:
            success, message = GameManagementService.add_game_to_user_collection(user, game)
            return Response({
                "status": "success" if success else "error",
                "message": message,
                "code": "game_added" if success else "game_exists",
                "game": {
                    "slug": game.slug,
                    "name": game.name
                }
            }, status=200 if success else 400)
        else:
            return Response({
                "status": "success",
                "message": "Game data retrieved successfully",
                "code": "game_retrieved",
                "game": {
                    "slug": game.slug,
                    "name": game.name
                }
            }, status=200)
        
class UserGames(APIView):
    """
    Класс для получения списка игр пользователя
    Требует аутентификации через JWT
    GET: возвращает все игры в коллекции пользователя
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Получение списка всех игр пользователя с их статусами и рейтингами"""
        user = request.user
        games = UserGame.objects.filter(user=user)
        serializer = UserGameSerializer(games, many=True)
        return Response(serializer.data, status=200)
    
    # Удаление игры из коллекции пользователя
    def post(self, request):
        slug = request.data.get('slug')
        success, message = GameManagementService.remove_game_from_user_collection(request.user, slug)
        print(success, message)
        return Response({
            "status": "error" if not success else "success",
            "message": message,
            "code": "game_not_found" if not success else "game_removed",
        }, status=200 if success else 400)
        
    # Изменение статуса игры
    def put(self, request):
        user = request.user
        slug = request.data.get('slug')
        status = request.data.get('status')
        success, message = GameManagementService.update_game_status(user, slug, status)
        return Response({
            "status": "error" if not success else "success",
            "message": message,
            "code": "game_not_found" if not success else "game_status_updated",
        }, status=200 if success else 400)

class ChangeGameScore(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        user = request.user
        raiting = request.data.get('raiting')
        success, message = GameManagementService.update_game_raiting(user, slug, raiting)
        return Response({
            "status": "error" if not success else "success",
            "message": message,
            "code": "game_not_found" if not success else "game_raiting_updated",
        }, status=200 if success else 400)

class RecomendedGames(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # Получение рекомендованных игр
    def get(self, request):
        user = request.user
        top_genres = RecomendedGamesService.get_favorite_genres(user)
        games = RecomendedGamesService.get_recomended_games(user, top_genres)
        user_game_slugs = UserGame.objects.filter(user=user).values_list('game__slug', flat=True)
        filtered_games = RecomendedGamesService.filter_games(games, user_game_slugs)

        # sorted_games = sorted(filtered_games, key=lambda game: game.get('metacritic', 0) or 0, reverse=True)            
        serializer = GameListSerializer(data=filtered_games[:10], many=True)  
        if serializer.is_valid():
            return Response(serializer.data, status=200)
            
        return Response(status=400)