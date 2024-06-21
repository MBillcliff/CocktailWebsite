from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Exists, OuterRef, Subquery, Case, When, Q, IntegerField, F
from .forms import RecipeForm, RecipeIngredientForm
from .models import Recipe, IngredientQuantity, LikedRecipe, RecipeRating, FavouriteRecipe, MadeRecipe
from accounts.models import Following
from ingredients.models import Ingredient, InStock
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.middleware.csrf import get_token

def annotate_recipe_queryset(qs, user):
	# Annotations to check if recipe is liked, favorite, or made by the user
	ingredients_in_stock = InStock.objects.filter(user=user, in_stock=True).values('ingredient_id')
	qs = qs.annotate(
		num_ingredients=Count('ingredientquantity'),
		liked=Exists(LikedRecipe.objects.filter(user=user, recipe=OuterRef('pk'))),
		favourite=Exists(FavouriteRecipe.objects.filter(user=user, recipe=OuterRef('pk'))),
		made=Exists(MadeRecipe.objects.filter(user=user, recipe=OuterRef('pk'))),
		num_ingredients_in_stock=Subquery(
			IngredientQuantity.objects.filter(
				recipe=OuterRef('pk'),  # Match recipe ID
				ingredient_id__in=ingredients_in_stock  # Filter by ingredients in stock
			).values('recipe').annotate(count=Count('ingredient_id')).values('count')[:1]
		)
	)
	return qs


@login_required
def delete_ingredient_view(request, id):
	ingredient = IngredientQuantity.objects.get(pk=id)
	recipe_id = ingredient.recipe.id
	ingredient.delete()
	return redirect(f"/recipes/{recipe_id}/edit/")


@login_required
def delete_recipe_view(request, id=None):
	if id is not None:
		recipe = Recipe.objects.get(pk=id)
		recipe.delete()
	return redirect(request.META.get('HTTP_REFERER'))


@login_required
def recipe_list_created_view(request):
	user = request.user

	qs = Recipe.objects.filter(created_by=request.user)
	qs = annotate_recipe_queryset(qs, user)

	# Determine which button was clicked and filter accordingly
	filter_by = request.GET.get('filter_by')  # Get the filter parameter from URL
	
	if filter_by == 'liked':
		qs = qs.filter(liked=True)
	elif filter_by == 'favourite':
		qs = qs.filter(favourite=True)
	elif filter_by == 'made':
		qs = qs.filter(made=True)
	
	no_content_message = "Oops... It appears you haven't created any of your own cocktails yet. Click 'Create New Cocktail' to get started." if len(qs) == 0 else ""
	context = {
		"object":qs,
		"no_content_message": no_content_message,
		"filter_by": filter_by,
	}
	return render(request, "recipes/list.html", context)

@login_required
def recipe_list_following_view(request):
	user=request.user
	following=[i.followed for i in Following.objects.filter(follower=request.user)]
	following.append(user)
	qs = Recipe.objects.filter(created_by__in=following)

	qs = annotate_recipe_queryset(qs, user)

	context = {
		"object":qs
	}
	return render(request, "recipes/list.html", context)

@login_required
def recipe_list_all_view(request):
	user = request.user

	# Initial queryset
	qs = Recipe.objects.all().order_by('name')
	qs = annotate_recipe_queryset(qs, user)

	# Determine which button was clicked and filter accordingly
	filter_by = request.GET.get('filter_by')  # Get the filter parameter from URL
	
	if filter_by == 'liked':
		qs = qs.filter(liked=True)
	elif filter_by == 'favourite':
		qs = qs.filter(favourite=True)
	elif filter_by == 'made':
		qs = qs.filter(made=True)
	
	context = {
		"object": qs,
		"filter_by": filter_by,  # Pass filter_by to template to highlight active button
	}
	return render(request, "recipes/list.html", context)

@login_required
def recipe_detail_view(response, id=None):
	obj = get_object_or_404(Recipe, id=id)

	ingredients =  Ingredient.objects.filter(ingredientquantity__recipe=obj).annotate(
	    quantity=F('ingredientquantity__quantity'),
	    unit=F('ingredientquantity__unit')
	)

	like_exists = LikedRecipe.objects.filter(user_id=response.user.id, recipe_id=id).exists()
	favourite_exists = FavouriteRecipe.objects.filter(user_id=response.user.id, recipe_id=id).exists()
	made_exists = MadeRecipe.objects.filter(user_id=response.user.id, recipe_id=id).exists()

	user_stock = [Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=response.user) if i.in_stock]

	context = {
		"object":obj,
		"ingredients":ingredients,
		"like_exists": like_exists,
		"favourite_exists": favourite_exists,
		"made_exists": made_exists,
		"in_stock": user_stock,
	}
	return render(response, "recipes/detail.html", context)

@login_required
def recipe_create_view(request, id=None):
	form = RecipeForm(request.POST or None)
	message="Create"

	if form.is_valid():
		new_form = form.save(commit=False)
		new_form.created_by_id = request.user.id
		new_form.save()
		return redirect(f"/recipes/{new_form.id}/edit/")

	context = {
		"form":form,
		"message":message
		}

	return render(request, "recipes/create-update.html", context)

@login_required
def recipe_update_view(request, id=None):
	obj = get_object_or_404(Recipe, id=id, created_by=request.user)
	ingredients = IngredientQuantity.objects.filter(recipe=obj)
	message="Edit"

	if request.method == 'POST':
		if 'quantity' in request.POST:
			ingredient_form = RecipeIngredientForm(request.POST or None)
			if ingredient_form.is_valid():
				form = ingredient_form.save(commit=False)
				form.recipe = obj
				form.save()
				ingredient_form = RecipeIngredientForm()
			form = RecipeForm(instance=obj)
		elif 'description' in request.POST:
			form = RecipeForm(request.POST or None, instance=obj)
			if form.is_valid():
				form.save()
				return redirect("/recipes/")
			ingredient_form = RecipeIngredientForm()
	else:
		form = RecipeForm(instance=obj)
		ingredient_form = RecipeIngredientForm()

	context = {
		"form":form,
		"ingredient_form":ingredient_form,
		"object":obj,
		"ingredients":ingredients,
		"message":message
		}

	return render(request, "recipes/create-update.html", context)


@login_required
def recipe_can_make_view(request):
	user=request.user
	qs=[]
	cocktails = Recipe.objects.all()
	cocktails = cocktails.annotate(num_ingredients=Count('ingredientquantity'))
	stock = [Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]
	for c in cocktails:
		ingredients = [i.ingredient for i in IngredientQuantity.objects.filter(recipe=c)]
		if all([ingredient in stock for ingredient in ingredients]):
			qs.append(c)

	no_content_message = "Uh oh... It appears there aren't any cocktails you can make right now. Try adding more ingredients or creating a new cocktail." if len(qs) == 0 else ""
	
	qs = Recipe.objects.filter(pk__in=[c.pk for c in qs])
	qs = annotate_recipe_queryset(qs, user)

	# Determine which button was clicked and filter accordingly
	filter_by = request.GET.get('filter_by')  # Get the filter parameter from URL
	
	if filter_by == 'liked':
		qs = qs.filter(liked=True)
	elif filter_by == 'favourite':
		qs = qs.filter(favourite=True)
	elif filter_by == 'made':
		qs = qs.filter(made=True)

	filter_message = f"There are {len(qs)} cocktails you can make with your current stock"

	context={"object": qs,
			"no_content_message": no_content_message,
			"filter_by": filter_by,
			"filter_message": filter_message,
			}
	
	return render(request, "recipes/list.html", context)


@login_required
def recipe_filter_by_ingredient_view(request, ingredient_id=None):
	user=request.user
	obj = get_object_or_404(Ingredient, id=ingredient_id)
	ingredient_quantity_qs = IngredientQuantity.objects.filter(ingredient_id=ingredient_id).values('recipe_id')
	recipes_with_ingredient = Recipe.objects.filter(id__in=Subquery(ingredient_quantity_qs))

	qs = annotate_recipe_queryset(recipes_with_ingredient, user)

	# Determine which button was clicked and filter accordingly
	filter_by = request.GET.get('filter_by')  # Get the filter parameter from URL
	
	if filter_by == 'liked':
		qs = qs.filter(liked=True)
	elif filter_by == 'favourite':
		qs = qs.filter(favourite=True)
	elif filter_by == 'made':
		qs = qs.filter(made=True)

	no_content_message = f"There currently aren't any cocktails with {obj.name}. Why not make your own?" if len(qs) == 0 else ""
	filter_message = f"Showing the {len(qs)} cocktail{'s' if len(qs)!=1 else ''} made with" if len(qs) != 0 else "There are no cocktails made with"

	user_stock = [Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]

	context = {
		"object":qs,
		"filter_message": filter_message,
		"filter_by": filter_by,
		"no_content_message": no_content_message,
		"ingredient": [obj],
		"in_stock": user_stock,
	}
	return render(request, "recipes/list.html", context)


def recipe_home_view(request):
	return render(request, "recipes/home.html")
	

def like_recipe_view(request, id):
	if request.method == "POST":
		user = request.user
		recipe=Recipe.objects.get(id=id)
		try:
			like = LikedRecipe.objects.get(recipe=recipe, user=user)
			like.delete()
			http = "<button type='submit' class='icon-button' id='{recipe_id}'><i class='fas fa-thumbs-up white'></i></button>".format(recipe_id=id)
		except LikedRecipe.DoesNotExist:
			LikedRecipe.objects.create(recipe=recipe, user=user)
			http = "<button type='submit' class='icon-button' id='{recipe_id}'><i class='fas fa-thumbs-up green'></i></button>".format(recipe_id=id)
	
	csrf_token = get_token(request)
	token_input = "<input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>".format(csrf_token=csrf_token)
	
	http = "<form method='POST' action='/recipes/like/{recipe_id}/' hx-post='/recipes/like/{recipe_id}/' hx-swap='outerHTML'>".format(recipe_id=id) + token_input + http + "</form>"

	return HttpResponse(http)


def favourite_recipe_view(request, id):
	if request.method == "POST":
		user = request.user
		recipe=Recipe.objects.get(id=id)
		try:
			like = FavouriteRecipe.objects.get(recipe=recipe, user=user)
			like.delete()
			http = "<button type='submit' class='icon-button' id='{recipe_id}'><i class='fas fa-heart white'></i></button>".format(recipe_id=id)
		except FavouriteRecipe.DoesNotExist:
			FavouriteRecipe.objects.create(recipe=recipe, user=user)
			http = "<button type='submit' class='icon-button' id='{recipe_id}'><i class='fas fa-heart red'></i></button>".format(recipe_id=id)
	
	csrf_token = get_token(request)
	token_input = "<input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>".format(csrf_token=csrf_token)
	
	http = "<form method='POST' action='/recipes/favourite/{recipe_id}/' hx-post='/recipes/favourite/{recipe_id}/' hx-swap='outerHTML'>".format(recipe_id=id) + token_input + http + "</form>"

	return HttpResponse(http)

def made_recipe_view(request, id):
	if request.method == "POST":
		user = request.user
		recipe=Recipe.objects.get(id=id)
		try:
			like = MadeRecipe.objects.get(recipe=recipe, user=user)
			like.delete()
			http = "<button type='submit' class='icon-button' id='{recipe_id}'><i class='fas fa-martini-glass white'></i></button>".format(recipe_id=id)
		except MadeRecipe.DoesNotExist:
			MadeRecipe.objects.create(recipe=recipe, user=user)
			http = "<button type='submit' class='icon-button' id='{recipe_id}'><i class='fas fa-martini-glass yellow'></i></button>".format(recipe_id=id)
	
	csrf_token = get_token(request)
	token_input = "<input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>".format(csrf_token=csrf_token)
	
	http = "<form method='POST' action='/recipes/made/{recipe_id}/' hx-post='/recipes/made/{recipe_id}/' hx-swap='outerHTML'>".format(recipe_id=id) + token_input + http + "</form>"

	return HttpResponse(http)

def rate_recipe_view(request, id, rating):
	rating = RecipeRating(recipe=Recipe.objects.get(pk=id), rating=rating)
	rating.save()
	return redirect(request.META.get('HTTP_REFERER'))