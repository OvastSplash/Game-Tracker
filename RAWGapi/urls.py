from django.urls import path
from .views import GameList, GetGame

urlpatterns = [
    path('gameList/<str:GameName>/', GameList.as_view(), name='game_list'),
    path('game/<str:GameName>/', GetGame.as_view(), name='game'),
]