from django.urls import path
from .views import GameList, GetGame, UserGames

urlpatterns = [
    path('gameList/<str:GameName>/', GameList.as_view(), name='game_list'),
    path('game/<str:GameName>/', GetGame.as_view(), name='game'),
    path('user/games/', UserGames.as_view(), name='user_games_api'),
]