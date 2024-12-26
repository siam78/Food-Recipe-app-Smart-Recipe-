from django.db import models
from .models import Recipe

class CleanUpRecipesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path == '/dashboard/':
            self.clean_up_recipes()
        return response

    def clean_up_recipes(self):
        recipes_to_keep = Recipe.objects.filter(
            models.Q(history_of__isnull=False) | 
            models.Q(favorited_by__isnull=False)
        ).distinct()
        Recipe.objects.exclude(id__in=recipes_to_keep).delete()