from rest_framework import serializers
from .models import UserGame

class PlatformDetailSerializer(serializers.Serializer):
    name = serializers.CharField()

class PlatformSerializer(serializers.Serializer):
    platform = PlatformDetailSerializer()

class StoreDetailSerializer(serializers.Serializer):
    name = serializers.CharField()

class StoreSerializer(serializers.Serializer):
    store = StoreDetailSerializer()

class GenreSerializer(serializers.Serializer):
    name = serializers.CharField()

class GameListSerializer(serializers.Serializer):
    name = serializers.CharField()
    released = serializers.CharField(allow_null=True)
    metacritic = serializers.IntegerField(allow_null=True)
    background_image = serializers.URLField(allow_null=True)
    platforms = PlatformSerializer(many=True, allow_null=True)
    stores = StoreSerializer(many=True, allow_null=True)
    genres = GenreSerializer(many=True, allow_null=True)
    slug = serializers.CharField()
    
    
class UpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGame
        fields = ['status']
        
    def validate_status(self, value):
        valid_statuses = [status[0] for status in UserGame.STATUS_CHOICES]
        
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status: {value}")
        
        return value