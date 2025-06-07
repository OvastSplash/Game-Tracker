from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from .serializers import GameListSerializer
from .create_serializers import GameSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Game
import requests

API_TOKEN = "d9a8b90eeff74d07905834091352b8c7"
User = get_user_model()

class GameList(APIView):
    def get(self, request, GameName):
        url = f"https://api.rawg.io/api/games?search={GameName}&key={API_TOKEN}&page_size=5"

        response = requests.get(url)
        data = response.json()
        games = data.get('results', [])
        
        sorted_games = sorted(games, key=lambda x: x.get('metacritic', 0) or 0, reverse=True)
        
        serializer = GameListSerializer(data=sorted_games, many=True)
        if serializer.is_valid():
            return Response(serializer.data)
        
        return Response(serializer.errors, status=400)
    
class GetGame(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # Get Game
    def get(self, request, GameName):
        url = f"https://api.rawg.io/api/games/{GameName}?key={API_TOKEN}"
        response = requests.get(url)
        data = response.json()
        print(data)
        serializer = GameListSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        
        return Response(serializer.errors, status=400)
    
    # Create Game
    def post(self, request, GameName):
        user_id = request.user.id
        print("User ID:", user_id)
        user = User.objects.get(id=user_id)
        print("User:", user)
        try:
            game = Game.objects.get(slug=GameName)
        except Game.DoesNotExist:
            game = None
        
        if game:
            if user.games.filter(slug=GameName).exists():
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
                user.games.add(game)
                return Response({
                    "status": "success",
                    "message": "Game successfully added to your collection",
                    "code": "game_added",
                    "game": {
                        "slug": game.slug,
                        "name": game.name
                    }
                }, status=201)

        url = f"https://api.rawg.io/api/games/{GameName}?key={API_TOKEN}"
        print(request.user)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            serializer = GameSerializer(data=data)
            if serializer.is_valid():
                game = serializer.save()
                user.games.add(game)
                return Response({
                    "status": "success",
                    "message": "Game successfully added to your collection",
                    "code": "game_added",
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