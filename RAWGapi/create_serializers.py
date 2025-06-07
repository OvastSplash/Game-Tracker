from rest_framework import serializers
from .models import Game, Platform, Store, Genre, Developer

class PlatformDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []}
        }

class PlatformSerializer(serializers.Serializer):
    platform = PlatformDetailSerializer()

class StoreDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []}
        }

class StoreSerializer(serializers.Serializer):
    store = StoreDetailSerializer()

class GenreModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []}
        }

class DeveloperModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []}
        }
        

class GameSerializer(serializers.ModelSerializer):
    platforms = PlatformSerializer(many=True)
    stores = StoreSerializer(many=True)
    genres = GenreModelSerializer(many=True)
    developers = DeveloperModelSerializer(many=True, allow_null=True)
    slug = serializers.SlugField(required=False)
    background_image = serializers.URLField(required=False, source='logo')
    
    class Meta:
        model = Game
        fields = '__all__'
        
    def create(self, validated_data):
        platforms_data = validated_data.pop('platforms')
        stores_data = validated_data.pop('stores')
        genres_data = validated_data.pop('genres')
        developer_data = validated_data.pop('developers')
        
        game = Game.objects.create(**validated_data)
        
        for platform_data in platforms_data:
            platform_name = platform_data['platform']['name']
            platform, created = Platform.objects.get_or_create(name=platform_name)
            game.platforms.add(platform)
        
        for store_data in stores_data:
            store_name = store_data['store']['name']
            store, created = Store.objects.get_or_create(name=store_name)
            game.stores.add(store)
            
        for genre_data in genres_data:
            genre_name = genre_data['name']
            genre, created = Genre.objects.get_or_create(name=genre_name)
            game.genres.add(genre)
            
        for dev_data in developer_data:
            dev_name = dev_data['name']
            developer, created = Developer.objects.get_or_create(name=dev_name)
            game.developers.add(developer)
            
        return game