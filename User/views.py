from typing import Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserLoginForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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
