from django.shortcuts import render
from recipes.models import Recipe
from ingredients.models import Ingredient, InStock
from django.contrib.auth.models import User
from itertools import chain
from accounts.models import Following
from django.db.models import Count, Subquery, OuterRef
from django.db.models.functions import Coalesce
from recipes.views import annotate_recipe_queryset

def search_all_view(request, searched=None):
    context = {}
    if request.method == 'POST':
        searched = request.POST['searched']

    if searched is not None:	    
        recipes = Recipe.objects.filter(name__contains=searched)
        recipes = annotate_recipe_queryset(recipes, request.user)
        
        ingredients = Ingredient.objects.filter(name__contains=searched)
        in_stock=[Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]
        members = User.objects.filter(username__contains=searched)

        # Retrieve the count of followers for each member
        followers_count_subquery = Following.objects.filter(followed=OuterRef('pk')).values('followed').annotate(followers_count=Count('follower'))
        members_with_followers = members.annotate(followers_count=Coalesce(Subquery(followers_count_subquery.values('followers_count')[:1]), 0))

        # Retrieve the count of people each member is following
        following_count_subquery = Following.objects.filter(follower=OuterRef('pk')).values('follower').annotate(following_count=Count('followed'))
        members_with_followers_and_following = members_with_followers.annotate(following_count=Coalesce(Subquery(following_count_subquery.values('following_count')[:1]), 0))
        
        objects = sorted(
            chain(recipes, ingredients, members_with_followers_and_following),
            key=lambda obj: obj.name.lower() if hasattr(obj, 'name') else obj.username.lower())
        selected = "all"
        context = {
            "searched": searched,
            "objects": objects,
            "recipes": recipes,
            "ingredients": ingredients,
            "members": members,
            "selected": selected,
            "in_stock": in_stock,
        }
    
    return render(request, "search/search.html", context)
	

def search_recipe_view(request, searched=None):
    context = {}
    if searched is not None:
        recipes = Recipe.objects.filter(name__contains=searched)
        recipes = annotate_recipe_queryset(recipes, request.user)
        selected = "recipes"
        context = {
			"searched": searched,
			"objects": recipes,
			"recipes": recipes,
            "selected": selected,
		}
		
    return render(request, "search/search.html", context)

	
def search_ingredient_view(request, searched=None):
    context = {}
    if searched is not None:
        ingredients = Ingredient.objects.filter(name__contains=searched)
        in_stock=[Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]
        selected="ingredients"
        context = {
			"searched": searched,
			"objects": ingredients,
			"ingredients": ingredients,
            "selected": selected,
            "in_stock": in_stock,
		}
		
    return render(request, "search/search.html", context)


def search_member_view(request, searched=None):
    context = {}
    if searched is not None:
        members = User.objects.filter(username__contains=searched)
        selected = "members"

        # Retrieve the count of followers for each member
        followers_count_subquery = Following.objects.filter(followed=OuterRef('pk')).values('followed').annotate(followers_count=Count('follower'))
        members_with_followers = members.annotate(followers_count=Coalesce(Subquery(followers_count_subquery.values('followers_count')[:1]), 0))

        # Retrieve the count of people each member is following
        following_count_subquery = Following.objects.filter(follower=OuterRef('pk')).values('follower').annotate(following_count=Count('followed'))
        members_with_followers_and_following = members_with_followers.annotate(following_count=Coalesce(Subquery(following_count_subquery.values('following_count')[:1]), 0))
        context = {
            "searched": searched,
            "objects": members_with_followers_and_following,
            "members": members,
            "selected": selected,
        }
    
    return render(request, "search/search.html", context)
	
