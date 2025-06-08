from typing import Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
class UserRegistrationView(CreateView):
    template_name = 'User/registration.html'
    form_class = UserRegistrationForm
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        
        return render(request, self.template_name, {'form': form})
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
class UserLoginView(CreateView):
    template_name = 'User/login.html'
    form_class = UserLoginForm
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            login_value = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            user = authenticate(request, login=login_value, password=password)
                        
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
                request.session['tokens'] = tokens
                return redirect('profile/')
            
                            
        return render(request, self.template_name, {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class CustomLogoutView(View):
    def post(self, request):
        """
        Кастомный logout view, который работает с AJAX запросами
        """
        try:
            # Выходим из системы
            logout(request)
            
            # Очищаем токены из сессии
            if 'tokens' in request.session:
                del request.session['tokens']
            
            return JsonResponse({
                'status': 'success',
                'message': 'Вы успешно вышли из аккаунта'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Ошибка при выходе: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """
        GET запрос для обычного выхода (без AJAX)
        """
        logout(request)
        return redirect('login')
