from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    image = models.URLField()
    nutrition_info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_recipes = models.ManyToManyField(Recipe, related_name='favorited_by', blank=True)
    recipe_history = models.ManyToManyField(Recipe, related_name='history_of', blank=True)

    def __str__(self):
        return self.user.username