from django.contrib import admin
from .models import Recipe, UserProfile

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'url', 'image')  # Add the fields you want to display in the list view
    search_fields = ('title',)  # Add fields to be searchable in the admin search bar
    list_filter = ('created_at',)  # Add filters for specific fields like created_at
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_count', 'get_history_count')
    search_fields = ('user__username',)
    
    def get_favorite_count(self, obj):
        return obj.favorite_recipes.count()
    get_favorite_count.short_description = 'Favorite Recipes'
    
    def get_history_count(self, obj):
        return obj.recipe_history.count()
    get_history_count.short_description = 'History Count'
