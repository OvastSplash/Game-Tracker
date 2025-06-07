from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

# Create your models here.

class Platform(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    
    def __str__(self):
        return self.name
    
class Store(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    
    def __str__(self):
        return self.name
    
class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name
    
class Developer(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    
    def __str__(self):
        return self.name

class Game(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    slug = models.SlugField(unique=True, null=True)
    platforms = models.ManyToManyField(Platform, related_name="platforms")
    stores = models.ManyToManyField(Store, related_name="stores")
    genres = models.ManyToManyField(Genre, related_name="genres")
    description = models.TextField(null=True)
    release_date = models.CharField(null=True)
    logo = models.URLField(max_length=255, null=True)
    developers = models.ManyToManyField(Developer, related_name="developers", blank=True)
    
    # rating is a integer between 0 and 100
    metacritic = models.IntegerField(null=True)
    
    def __str__(self):
        return self.name
    
class UserGame(models.Model):
    STATUS_CHOICES = [
        ('PLAN_TO_PLAY', 'Планирую пройти'),
        ('PLAYING', 'Прохожу'),
        ('COMPLETED', 'Пройдена'),
    ]
    
    user = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='PLAN_TO_PLAY',
    )
    
    user_raiting = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    
    added_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'game')
        
    def __str__(self):
        return f"{self.user.login} - {self.game.name}"
    
    def is_completed(self):
        return self.status == 'COMPLETED'
    
    def is_playing(self):
        return self.status == 'PLAYING'
    
    def is_plan_to_play(self):
        return self.status == 'PLAN_TO_PLAY'
