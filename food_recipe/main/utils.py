import boto3
from django.conf import settings
import requests

FOOD_LABELS = [
    # Vegetables
    'Potato', 'Onion', 'Garlic', 'Ginger', 'Tomato', 'Eggplant', 'Pumpkin', 
    'Spinach', 'Mustard Greens', 'Cabbage', 'Cauliflower', 'Bitter Gourd', 
    'Bottle Gourd', 'Ridge Gourd', 'Drumstick', 'Carrot', 'Green Beans', 
    'Okra', 'Radish', 'Turnip', 'Green Chilies', 'Zucchini', 'Broccoli', 
    'Asparagus', 'Lettuce', 'Kale', 'Celery', 'Artichoke', 'Leek', 'Swiss Chard', 
    'Brussels Sprouts', 'Avocado', 'Bell Pepper', 'Snow Peas', 'Edamame', 
    'Mushroom', 'Sweet Potato', 'Beetroot', 'Corn', 'Spring Onion',

    # Lentils and Pulses
    'Red Lentils', 'Yellow Lentils', 'Pigeon Peas', 'Bengal Gram', 'Black Gram', 'Split Peas',

    # Grains
    'Rice', 'Basmati Rice', 'Parboiled Rice', 'Wheat', 'Flour', 'Quinoa', 
    'Barley', 'Millet', 'Couscous', 'Oats', 'Buckwheat',

    # Spices
    'Cumin', 'Coriander', 'Turmeric', 'Red Chili Powder', 'Green Cardamom', 
    'Black Cardamom', 'Cloves', 'Cinnamon', 'Nutmeg', 'Mace', 'Fenugreek Seeds', 
    'Mustard Seeds', 'Fennel Seeds', 'Nigella Seeds', 'Black Pepper', 'Bay Leaf', 
    'Asafoetida', 'Paprika', 'Saffron', 'Thyme', 'Rosemary', 'Oregano', 
    'Basil', 'Parsley', 'Dill', 'Chives', 'Tarragon',

    # Protein Sources
    'Chicken', 'Mutton', 'Beef', 'Fish', 'Egg', 'Paneer', 'Tofu', 'Tempeh',

    # Dairy Products
    'Milk', 'Yogurt', 'Ghee', 'Butter', 'Cream', 'Cheddar', 'Mozzarella', 
    'Parmesan', 'Blue Cheese', 'Ricotta',

    # Oils
    'Mustard Oil', 'Sunflower Oil', 'Coconut Oil', 'Olive Oil', 'Sesame Oil', 
    'Canola Oil', 'Avocado Oil',

    # Fruits
    'Mango', 'Banana', 'Guava', 'Papaya', 'Coconut', 'Tamarind', 'Lemon', 
    'Lime', 'Apple', 'Orange', 'Grapes', 'Strawberry', 'Pineapple', 'Kiwi', 
    'Pomegranate', 'Watermelon', 'Blueberry', 'Raspberry', 'Blackberry', 
    'Cherry', 'Peach', 'Pear', 'Plum', 'Apricot', 'Fig', 'Date', 'Dragon Fruit', 
    'Passion Fruit', 'Lychee', 'Mangosteen', 'Durian', 'Starfruit', 'Pomelo', 
    'Cranberry', 'Cantaloupe', 'Honeydew Melon', 'Avocado',

    # Herbs
    'Coriander Leaves', 'Mint Leaves', 'Curry Leaves', 'Fenugreek Leaves', 
    'Sage', 'Basil', 'Parsley', 'Rosemary', 'Oregano', 'Dill', 'Chives', 'Tarragon',

    # Nuts and Seeds
    'Almonds', 'Cashews', 'Raisins', 'Sesame Seeds', 'Poppy Seeds', 
    'Chia Seeds', 'Flax Seeds', 'Pumpkin Seeds', 'Sunflower Seeds', 'Walnuts', 
    'Pecans', 'Hazelnuts', 'Macadamia Nuts', 'Brazil Nuts',

    # Others
    'Tamarind Pulp', 'Jaggery', 'Sugar', 'Salt', 'Vinegar', 'Baking Soda', 
    'Baking Powder', 'Soy Sauce', 'Fish Sauce', 'Hoison Sauce', 'Coconut Milk'
]


def detect_ingredients(image):
    client = boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    response = client.detect_labels(Image={'Bytes': image.read()}, MaxLabels=10)
    ingredients = [label['Name'] for label in response['Labels']
                   if label['Name'] in FOOD_LABELS and label['Confidence'] > 80
    ]
    return ingredients

def get_recipes_with_nutrition(ingredients):
    api_key = settings.SPOONACULAR_API_KEY
    url = f"https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'apiKey': api_key,
        'cuisine': 'Indian',
        'includeIngredients': ','.join(ingredients),
        'addRecipeInformation': True,
        'addRecipeNutrition': True,
        'number': 10
    }
    response = requests.get(url, params=params)
    recipes = response.json().get('results', [])
    for recipe in recipes:
        #recipe['nutrition'] = recipe.get('nutrition', {}).get('nutrients', [])
        nutrients = recipe.get('nutrition', {}).get('nutrients', [])
        
        # Map the nutrients to a cleaner format with name, amount, and unit
        formatted_nutrients = [
            {
                'name': nutrient.get('name', 'Unknown Nutrient'),
                'amount': nutrient.get('amount', 0),
                'unit': nutrient.get('unit', '')
            }
            for nutrient in nutrients
        ]
        
        # Add formatted nutrition data back into the recipe object
        recipe['nutrition'] = formatted_nutrients
    return recipes

