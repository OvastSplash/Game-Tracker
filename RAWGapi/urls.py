from django.urls import path
from .views import GameList, GetGame, GetUserGames

urlpatterns = [
    path('gameList/<str:GameName>/', GameList.as_view(), name='game_list'),
    path('game/<str:GameName>/', GetGame.as_view(), name='game'),
    path('user/games/', GetUserGames.as_view(), name='user_games_api'),
]