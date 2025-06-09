from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
        path('', views.Profile.as_view(), name='profile'),
        path('game/<str:GameSlug>/', views.Game.as_view(), name='game'),
        path('developer/<str:developer_name>/', views.Developer.as_view(), name='developer'),
] 