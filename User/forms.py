from django import forms
from .models import CustomUser
from django.contrib.auth import authenticate

class UserRegistrationForm(forms.ModelForm):
    login = forms.CharField(label="Логин", max_length=20)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    check_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    steam_id = forms.CharField(label="ID Steam (необязательно)", required=False)
    favorite_genre = forms.CharField(label="Любимый жанр (необязательно)", required=False)
    
    class Meta:
        model = CustomUser
        fields = ['login', 'password', 'check_password', 'steam_id', 'favorite_genre']
        
    def login_clean(self):
        login = self.cleaned_data.get("login")
        
        if login:
            if CustomUser.objects.filter(login=login).exists():
                raise forms.ValidationError("Пользователь с таким логином уже существует")
            return login
            
        else:
            raise forms.ValidationError("Логин не может быть пустым")
        
    def clean(self):
        password = self.cleaned_data.get("password")
        check_password = self.cleaned_data.get("check_password")
        
        if not password or not check_password:
            raise forms.ValidationError("Пароль не может быть пустым")
        
        if password != check_password:
            raise forms.ValidationError("Пароли не совпадают")
        
        return self.cleaned_data
    
    def clean_steam_id(self):
        steam_id = self.cleaned_data.get("steam_id")
        return steam_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password"))
        
        if commit:
            user.save()
        return user

class UserLoginForm(forms.ModelForm):
    login = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш логин',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['login', 'password']
        
    def clean(self):
        login = self.cleaned_data.get("login")
        password = self.cleaned_data.get("password")
        
        if login and password:
            user = authenticate(login=login, password=password)
            
            if user is None:
                raise forms.ValidationError("Неверный логин или пароль")
            
            if not user.is_active:
                raise forms.ValidationError("Аккаунт не активен")

        return self.cleaned_data