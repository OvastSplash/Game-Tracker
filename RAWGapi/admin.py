from django.contrib import admin
from .models import Game, Platform, Store, Genre, Developer, UserGame

# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'release_date', 'metacritic')
    list_filter = ('release_date', 'metacritic', 'genres')
    search_fields = ('name', 'slug')
    filter_horizontal = ('platforms', 'stores', 'genres', 'developers')
    readonly_fields = ('slug',)

@admin.register(UserGame)
class UserGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'status', 'user_raiting', 'added_at')
    list_filter = ('status', 'added_at', 'updated_at')
    search_fields = ('user__login', 'game__name')

admin.site.register(Platform)
admin.site.register(Store)
admin.site.register(Genre)
admin.site.register(Developer)