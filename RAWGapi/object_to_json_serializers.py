from rest_framework import serializers
from .models import Game, UserGame

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['name', 'slug', 'logo', 'metacritic']


class UserGameSerializer(serializers.ModelSerializer):
    game = GameSerializer()
    
    class Meta:
        model = UserGame
        fields = ['game', 'status', 'user_raiting', 'added_at', 'updated_at']