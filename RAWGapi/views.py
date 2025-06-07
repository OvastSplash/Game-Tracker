from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GameListSerializer, UpdateStatusSerializer
from .create_serializers import GameSerializer
from .object_to_json_serializers import UserGameSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Game, UserGame
from GameTracker.settings import RAWG_API_TOKEN
import requests

User = get_user_model()

class GameList(APIView):
    """
    Класс для поиска игр через RAWG API
    GET запрос возвращает топ-5 игр, отсортированных по рейтингу Metacritic
    """
    def get(self, request, GameName):
        # Формируем URL для поиска игр, ограничиваем 5 результатами
        url = f"https://api.rawg.io/api/games?search={GameName}&key={RAWG_API_TOKEN}&page_size=5"

        response = requests.get(url)
        data = response.json()
        games = data.get('results', [])
        
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
        url = f"https://api.rawg.io/api/games/{GameName}?key={RAWG_API_TOKEN}"
        response = requests.get(url)
        data = response.json()
        print(data)
        serializer = GameListSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        
        return Response(serializer.errors, status=400)
    
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
        user_id = request.user.id
        print("User ID:", user_id)
        user = User.objects.get(id=user_id)
        print("User:", user)
        
        # Проверяем, существует ли игра в нашей базе
        try:
            game = Game.objects.get(slug=GameName)
        except Game.DoesNotExist:
            game = None
        
        if game:
            addGame = request.data.get('addGame', True)
            
            if addGame:
                # Проверяем, есть ли уже эта игра у пользователя
                if UserGame.objects.filter(user=user, game=game).exists():
                    return Response({
                        "status": "error",
                        "message": "Game already exists in your collection",
                        "code": "game_exists",
                        "game": {
                            "slug": game.slug,
                            "name": game.name
                        }
                    }, status=400)
                else:
                    # Добавляем игру в коллекцию пользователя
                    UserGame.objects.create(user=user, game=game)
                    return Response({
                        "status": "success",
                        "message": "Game successfully added to your collection",
                        "code": "game_added",
                        "game": {
                            "slug": game.slug,
                            "name": game.name
                        }
                    }, status=201)
            else:
                # Просто возвращаем информацию об игре без добавления
                return Response({
                    "status": "success",
                    "message": "Game information retrieved successfully",
                    "code": "game_found",
                    "game": {
                        "slug": game.slug,
                        "name": game.name
                    }
                }, status=200)

        # Если игры нет в базе, получаем её из RAWG API
        url = f"https://api.rawg.io/api/games/{GameName}?key={RAWG_API_TOKEN}"
        print(request.user)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            serializer = GameSerializer(data=data)
            if serializer.is_valid():
                # Создаем новую игру и добавляем её пользователю
                game = serializer.save()
                
                addGame = request.data.get('addGame', True)
                if addGame:
                    UserGame.objects.create(user=user, game=game)

                    return Response({
                        "status": "success",
                        "message": "Game successfully added to your collection",
                        "code": "game_added",
                        "game": {
                            "slug": game.slug,
                            "name": game.name
                        }
                    }, status=201)
                    
                else:
                    return Response({
                        "status": "success",
                        "message": "Game successfully has been created",
                        "code": "game_created",
                        "game": {
                            "slug": game.slug,
                            "name": game.name
                        }
                    }, status=201)
        
        return Response({
            "status": "error",
            "message": "Failed to create game",
            "code": "creation_failed",
            "errors": serializer.errors if 'serializer' in locals() else {"detail": "Failed to fetch game data"}
        }, status=400)
        
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
        try:
            user = request.user
            game_slug = request.data.get('slug')
            
            game = UserGame.objects.filter(user=user).prefetch_related('game').get(game__slug=game_slug)
            game.delete()
            return Response(status=204)
        
        except UserGame.DoesNotExist:
            return Response(status=404)
        
        except Exception as e:
            return Response(status=500)
        
    # Изменение статуса игры
    def put(self, request):
        try:
            user = request.user
            game_slug = request.data.get('slug')
            status = request.data.get('status')
            serializer = UpdateStatusSerializer(data={'status': status})
            if serializer.is_valid():
                game = UserGame.objects.filter(user=user).prefetch_related('game').get(game__slug=game_slug)
                game.status = status
                game.save()
                
            else:
                return Response(serializer.errors, status=400)
                
            return Response(status=200)
        
        except UserGame.DoesNotExist:
            return Response(status=404)
        except Exception as e:
            return Response(status=500)
        
