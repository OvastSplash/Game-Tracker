from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserRegistrationView, UserLoginView 

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
