from django.shortcuts import render
from recipes.models import Recipe
from ingredients.models import Ingredient, InStock
from django.contrib.auth.decorators import login_required
from recipes.views import annotate_recipe_queryset
from datetime import datetime
# Create your views here.

def get_season(date):
    month = date.month
    
    # Define the seasons based on month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Autumn"


@login_required
def home_view(response):
	cocktail_names = {
	'Winter': ["Rum Toddy", "Gin Toddy", "Orange Scented Hot Chocolate"],
	'Spring': ["Cosmopolitan", "Gin Fizz", "Grand Blue"],
	'Summer': ["Margarita", "Absolut Summertime", "Tequila Sunrise"],
	'Autumn': ["Amaretto Stinger", "Manhatten", "Mocha-berry"],
	}
	
	current_date = datetime.now()
	current_season = get_season(current_date)
	print(current_season)
	seasonal_cocktail_names = cocktail_names[current_season]

	seasonal_cocktails = Recipe.objects.filter(name__in=seasonal_cocktail_names)
	seasonal_cocktails = annotate_recipe_queryset(seasonal_cocktails, response.user)

	popular_ingredient_names = ['Vodka', 'Rum', 'Gin', 'Tequila', 'Brandy', 'Whisky']
	popular_ingredients = Ingredient.objects.filter(name__in=popular_ingredient_names)

	user_stock = [Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=response.user) if i.in_stock]

	context={
		"seasonal_message": "It's Summer! Here are a few seasonal cocktails to get you started.",
		"seasonal_cocktails": seasonal_cocktails,
		"popular_ingredients": popular_ingredients,
	}

	return render(response, "main/home.html", context=context)
