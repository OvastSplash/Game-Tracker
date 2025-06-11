# GameTracker 🎮

Веб-приложение для отслеживания и управления коллекцией игр с интеграцией RAWG API и Steam API.

## 🚀 Возможности

- **Поиск игр** через RAWG API
- **Управление коллекцией** - добавление, удаление, изменение статуса игр
- **Система рейтингов** - оценка игр от 1 до 5 звезд
- **Персонализированные рекомендации** на основе ваших предпочтений
- **Статистика** - отслеживание прогресса по играм
- **JWT аутентификация** для безопасности

## 📋 Требования

- Python 3.8+
- Django 5.2.1
- Активный интернет (для работы с API)

## 🛠️ Установка

### 1. Клонирование репозитория
```bash
git clone <your-repo-url>
cd GameTracker
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создание суперпользователя (опционально)
```bash
python manage.py createsuperuser
```

## 🔧 Конфигурация

### Локальная разработка

1. **Скопируйте файл настроек:**
```bash
cp GameTracker/settings_local.py.example GameTracker/settings_local.py
```

2. **Отредактируйте `GameTracker/settings_local.py`:**
```python
# Ваши API ключи
SECRET_KEY = 'your-django-secret-key'
JWT_SECRET_KEY = 'your-jwt-secret-key'
RAWG_API_TOKEN = "your_rawg_api_key"
STEAM_API_TOKEN = "your_steam_api_key"

# Настройки разработки
DEBUG = True
```

### Production (Render.com)

📋 **Подробные инструкции по деплою см. в [RENDER_DEPLOY.md](RENDER_DEPLOY.md)**

Установите переменные окружения в Render Dashboard:
- `SECRET_KEY` - Django секретный ключ
- `JWT_SECRET_KEY` - JWT секретный ключ
- `RAWG_API_TOKEN` - Ваш RAWG API ключ
- `STEAM_API_TOKEN` - Ваш Steam API ключ
- `DEBUG=False` - Отключить режим отладки
- `DATABASE_URL` - URL базы данных PostgreSQL (создается автоматически)

**Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`

**Start Command:** `gunicorn GameTracker.wsgi:application`

## 🚀 Запуск

### Локальный запуск
```bash
python manage.py runserver
```

### Запуск для внешнего доступа
```bash
python manage.py runserver 0.0.0.0:8000
```

Приложение будет доступно по адресу:
- Локально: `http://localhost:8000`
- Внешний доступ: `http://your-ip:8000`

## 🔐 Настройка файервола (Windows)

Для внешнего доступа добавьте правило файервола:
```powershell
netsh advfirewall firewall add rule name="Django GameTracker" dir=in action=allow protocol=TCP localport=8000
```

## 📁 Структура проекта

```
GameTracker/
├── GameTracker/          # Основные настройки Django
├── User/                 # Приложение для аутентификации
├── RAWGapi/             # API для работы с играми
├── Profile/             # Профиль пользователя
├── SteamAPI/            # Интеграция с Steam
├── static/              # Статические файлы
├── templates/           # HTML шаблоны
├── requirements.txt     # Зависимости Python
└── manage.py           # Django команды
```

## 🎯 Использование

1. **Регистрация/Вход** - создайте аккаунт или войдите
2. **Поиск игр** - используйте поиск для нахождения игр
3. **Добавление в коллекцию** - добавляйте игры в свою библиотеку
4. **Управление статусами** - отмечайте как "Играю", "Завершено", "Планирую"
5. **Оценка игр** - ставьте рейтинг от 1 до 5 звезд
6. **Рекомендации** - получайте персональные рекомендации

## 🔧 API Endpoints

- `GET /api/games/{name}/` - поиск игр
- `POST /api/game/{slug}/` - добавление игры в коллекцию
- `GET /api/user/games/` - получение игр пользователя
- `PUT /api/user/games/` - изменение статуса игры
- `GET /api/user/recomended/` - получение рекомендаций

## 📱 Технологии

- **Backend**: Django 5.2.1, Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **База данных**: SQLite (по умолчанию)
- **API**: RAWG API, Steam API
- **Аутентификация**: JWT токены

## 🤝 Разработка

Для разработки рекомендуется:
1. Включить `DEBUG = True` в настройках
2. Использовать виртуальное окружение
3. Следовать PEP 8 для Python кода

## 📞 Поддержка

При возникновении проблем проверьте:
- Правильность API ключей
- Настройки файервола
- Версии Python и зависимостей
- Логи сервера Django

---

Создано с ❤️ для любителей игр 🎮 