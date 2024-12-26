from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db import models
from .models import Recipe, UserProfile
from .utils import detect_ingredients, get_recipes_with_nutrition
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, IngredientForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from .forms import UserProfileForm, PasswordChangeForm
import base64
from io import BytesIO

def welcome(request):
    if request.user.is_authenticated:
        return render(request, 'main/welcome.html')
    else:
        return redirect('login')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('login')
    return render(request, 'main/delete_account.html')

@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # Save the image data before processing
        image_data = BytesIO()
        for chunk in image.chunks():
            image_data.write(chunk)
        
        # Get base64 encoded image for display
        encoded_image = base64.b64encode(image_data.getvalue()).decode('utf-8')
        
        # Reset file pointer for detect_ingredients
        image_data.seek(0)
        detected_ingredients = detect_ingredients(image_data)
        
        form = IngredientForm(initial={'ingredients': ', '.join(detected_ingredients)})
        return render(request, 'main/ingredient_list.html', {
            'form': form,
            'uploaded_image': encoded_image
        })
    return render(request, 'main/upload.html')

@login_required
def search_recipes(request):
    if request.method == 'POST':
        print(request.POST)
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredients = [i.strip() for i in form.cleaned_data['ingredients'].split(',')]
            
            # Remove the filter for food items
            recipes = get_recipes_with_nutrition(ingredients)
            ingredients = [i.strip() for i in form.cleaned_data['ingredients'].split(',')]
            
            # Remove the filter for food items
            recipes = get_recipes_with_nutrition(ingredients)
            
            # Add IDs to recipes for frontend reference
            for i, recipe in enumerate(recipes):
                recipe['id'] = i + 1
            
            print(f"Ingredients received: {ingredients}")  # Debugging line
            # Store recipes in session
            request.session['recipes'] = recipes
            
            profile = UserProfile.objects.get(user=request.user)

            # Check if the user is authenticated
            '''
            if not request.user.is_authenticated:
                print("User is not authenticated")  # Debugging line
                return redirect('login')  # Redirect to login if not authenticated 
            '''
            for recipe_data in recipes:
                existing_recipes = Recipe.objects.filter(
                    title=recipe_data['title'],
                    url=recipe_data['sourceUrl'],
                    image=recipe_data['image'],
                    nutrition_info=recipe_data.get('nutrition')
                )
                
                if existing_recipes.exists():
                    recipe = existing_recipes.first()  # Use the first existing recipe
                else:
                    # Create new recipe if it doesn't exist
                    recipe = Recipe.objects.create(
                        title=recipe_data['title'],
                        url=recipe_data['sourceUrl'],
                        image=recipe_data['image'],
                        nutrition_info=recipe_data.get('nutrition')
                    )

                # Add the recipe to the user's history if it's not already there
                if not profile.recipe_history.filter(id=recipe.id).exists():
                    profile.recipe_history.add(recipe)
                #profile.recipe_history.add(recipe)

            if profile.recipe_history.count() > 3:
                excess = profile.recipe_history.count() - 3
                
                for recipe in profile.recipe_history.all()[:excess]:
                    profile.recipe_history.remove(recipe)

            return render(request, 'main/recipe_list.html', {'recipes': recipes, 'form': form})
        
    return redirect('upload_image')


@login_required
def toggle_favorite(request, recipe_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        recipes = request.session.get('recipes', [])
        recipe_data = next((r for r in recipes if r.get('id') == recipe_id), None)
        if recipe_data:
            recipe = Recipe.objects.create(
                title=recipe_data['title'],
                url=recipe_data['sourceUrl'],
                image=recipe_data['image'],
                nutrition_info=recipe_data.get('nutrition')
            )
        else:
            return JsonResponse({'status': 'error', 'message': 'Recipe not found'}, status=404)

    if recipe in profile.favorite_recipes.all():
        profile.favorite_recipes.remove(recipe)
        message = "Removed from favorites"
    else:
        profile.favorite_recipes.add(recipe)
        message = "Added to favorites"
    
    return JsonResponse({'status': 'success', 'message': message})
    #return JsonResponse({'message': message, 'status': 'success'})

@login_required
def user_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    history = profile.recipe_history.order_by('-id')[:3]
    
    # Debugging: Print the history to the console
    print(f"User: {request.user.username}, Recipe History: {[recipe.title for recipe in history]}")
    
    favorites = profile.favorite_recipes.all()
    return render(request, 'main/dashboard.html', {'history': history, 'favorites': favorites})

# User registration view
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Hash the password
            user.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})

# User login view
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = UserLoginForm()
    return render(request, 'main/login.html', {'form': form})

# User logout view
def user_logout(request):
    # Get all recipes that are either in someone's history or favorites
    recipes_to_keep = Recipe.objects.filter(
        models.Q(history_of__isnull=False) | 
        models.Q(favorited_by__isnull=False)
    ).distinct()
    
    # Delete all other recipes
    Recipe.objects.exclude(id__in=recipes_to_keep).delete()
    
    logout(request)
    return redirect('login')

@login_required
def edit_ingredients(request):
    form = IngredientForm()
    return render(request, 'main/ingredient_list.html', {'form': form})

# views.py
@login_required
def profile(request):
    profile_form = UserProfileForm(instance=request.user)
    password_form = PasswordChangeForm()
    return render(request, 'main/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=request.user)
    return render(request, 'main/profile.html', {'profile_form': profile_form})

@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.POST)
        if password_form.is_valid():
            old_password = password_form.cleaned_data['old_password']
            new_password = password_form.cleaned_data['new_password1']
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Old password is incorrect.')
    else:
        password_form = PasswordChangeForm()
    return render(request, 'main/profile.html', {'password_form': password_form})

@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, 'main/recipe_detail.html', {'recipe': recipe})

