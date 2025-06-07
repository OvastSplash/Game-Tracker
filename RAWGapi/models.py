from django.db import models

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
    release_date = models.DateField(null=True)
    logo = models.URLField(max_length=255, null=True)
    developers = models.ManyToManyField(Developer, related_name="developers", null=True, blank=True)
    
    # rating is a integer between 0 and 100
    metacritic = models.IntegerField(null=True)
    
    def __str__(self):
        return self.name
    
    def release_date(self):
        return self.release_date.strftime("%Y-%m-%d")
    
    