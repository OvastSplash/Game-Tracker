from django.urls import path
from .views import AuthSteamID

urlpatterns = [
    path('getId/<str:steam_id>/', AuthSteamID.as_view(), name='get_id'),
]
