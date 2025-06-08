from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserRegistrationView, UserLoginView, CustomLogoutView

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
