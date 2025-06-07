from django.contrib import admin
from .models import Game, Platform, Store, Genre, Developer

# Register your models here.
admin.site.register(Game)
admin.site.register(Platform)
admin.site.register(Store)
admin.site.register(Genre)
admin.site.register(Developer)
