from django.contrib import admin
from .models import Game, Platform, Store, Genre, Developer, UserGame

# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'release_date', 'metacritic', 'get_stores_count')
    list_filter = ('release_date', 'metacritic', 'genres', 'stores')
    search_fields = ('name', 'slug')
    filter_horizontal = ('platforms', 'stores', 'genres', 'developers')
    readonly_fields = ('slug',)
    
    def get_stores_count(self, obj):
        return obj.stores.count()
    get_stores_count.short_description = 'Количество магазинов'

@admin.register(UserGame)
class UserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status', 'user_raiting', 'added_at')
    list_filter = ('status', 'added_at', 'updated_at')
    search_fields = ('user__login', 'game__name')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_games_count')
    search_fields = ('name',)
    
    def get_games_count(self, obj):
        return obj.stores.count()
    get_games_count.short_description = 'Количество игр'

admin.site.register(Platform)
admin.site.register(Genre)
admin.site.register(Developer)