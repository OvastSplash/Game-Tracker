from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from datetime import datetime
from django.conf import settings

class JWTTokenRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and 'tokens' in request.session:
            try:
                # Декодируем access токен для проверки времени истечения
                access_token = request.session['tokens']['access']
                decoded_token = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
                
                # Получаем время истечения токена и делаем его timezone-aware
                exp_timestamp = decoded_token['exp']
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.get_current_timezone())
                
                # Если до истечения токена осталось менее 5 минут
                if (exp_datetime - timezone.now()).total_seconds() < 300:  # 5 минут
                    # Обновляем токены
                    refresh_token = RefreshToken(request.session['tokens']['refresh'])
                    request.session['tokens'] = {
                        'access': str(refresh_token.access_token),
                        'refresh': str(refresh_token),
                    }
                    
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
                # Если возникла ошибка при декодировании токена, пропускаем обновление
                pass
                
        response = self.get_response(request)
        return response 