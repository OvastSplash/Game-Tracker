from django.contrib.auth.backends import BaseBackend
from .models import CustomUser

# Здесь будет ваша реализация кастомной аутентификации 

class CustomBackend(BaseBackend):
    def authenticate(self, request, login=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(login=login)
            if user.check_password(password):
                return user
            
            else:
                return None
            
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None