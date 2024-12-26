from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('upload/', views.upload_image, name='upload_image'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('edit-ingredients/', views.edit_ingredients, name='edit_ingredients'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('toggle-favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('', views.welcome, name='welcome'),
]
