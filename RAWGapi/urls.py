from django.urls import path
from .views import GameList, GetGame, UserGames, RecomendedGames, ChangeGameScore

urlpatterns = [
    path('gameList/<str:GameName>/', GameList.as_view(), name='game_list'),
    path('game/<str:GameName>/', GetGame.as_view(), name='game'),
    path('user/games/', UserGames.as_view(), name='user_games_api'),
    path('user/recomended/', RecomendedGames.as_view(), name='recomended_games_api'),
    path('user/game/<str:slug>/', ChangeGameScore.as_view(), name='change_game_score_api'),
]