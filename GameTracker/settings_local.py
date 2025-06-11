# Локальные настройки - НЕ КОММИТИТЬ В GIT!

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i3#d1gjih(m%kr*6qtm3&0#(5i)2m8h9&4q*%(@57xlm6l#oie'

# API Tokens
JWT_SECRET_KEY = 'K8dj3*mN9$pL#vF5@qW2&hX4%tY7!zC1'
RAWG_API_TOKEN = "d9a8b90eeff74d07905834091352b8c7"
STEAM_API_TOKEN = "BE55382C90237E602B9743D97F7615D3"

# Debug settings
DEBUG = True

# Local database (для разработки)
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES_LOCAL = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
} 