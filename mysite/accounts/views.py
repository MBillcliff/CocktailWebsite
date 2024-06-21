from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .models import Following
from django.middleware.csrf import get_token
from django.db.models import Count, Subquery, OuterRef, Exists, IntegerField
from django.db.models.functions import Coalesce
from recipes.models import Recipe, FavouriteRecipe
from recipes.views import annotate_recipe_queryset
from ingredients.models import Ingredient, InStock


def register_view(response):
	if response.method == "POST":
		form = RegisterForm(response.POST)
		if form.is_valid():
			form.save()
			return redirect("/accounts/login/")
	else:
		form = RegisterForm()

	return render(response, "register/register.html", {"form": form})


@login_required
def my_profile_view(response):
	user = response.user
	followers = Following.objects.filter(followed=user.id)
	following = Following.objects.filter(follower=user.id)

	context={
		"followers": followers,
		"following": following,
		"member": user,
		}
	return render(response, "profile/my-profile.html", context)


@login_required
def member_profile_view(response, id=None):
	followers = Following.objects.filter(followed=id)
	following = Following.objects.filter(follower=id)

	member = User.objects.get(pk=id)
	user = response.user
	following_exists = Following.objects.filter(follower_id=user.id, followed_id=id).exists()

	created = Recipe.objects.filter(created_by=member)
	created = annotate_recipe_queryset(created, user)

	# Initial queryset
	favourites = Recipe.objects.all().order_by('name')
	favourites = annotate_recipe_queryset(favourites, user)
	favourites = favourites.annotate(
		member_favourite=Exists(FavouriteRecipe.objects.filter(user=member, recipe=OuterRef('pk'))),)
	
	favourites = favourites.filter(member_favourite=True)
	
	member_stock = ingredients = Ingredient.objects.filter(instock__user=member, instock__in_stock=True)
	user_stock = ingredients = Ingredient.objects.filter(instock__user=user, instock__in_stock=True)

	context={
		"followers": followers,
		"following": following,
		"member": member,
		"following_exists": following_exists,
		"member_recipes": created,
		"member_favourites": favourites, 
		"member_stock": member_stock,
		"in_stock": user_stock,
	}

	if id == response.user.id:
		return render(response, "profile/my-profile.html", context)
	
	return render(response, "profile/member-profile.html", context)



@login_required
def following_view(request, id=None):
	member = get_object_or_404(User, pk=id)
	following_ids = Following.objects.filter(follower_id=id).values_list('followed_id', flat=True)
	members = User.objects.filter(id__in=following_ids)
	
	followers_count_subquery = Following.objects.filter(followed=OuterRef('pk')).values('followed').annotate(followers_count=Count('follower'))
	following_count_subquery = Following.objects.filter(follower=OuterRef('pk')).values('follower').annotate(following_count=Count('followed'))
	
	members = members.annotate(
		followers_count=Subquery(followers_count_subquery.values('followers_count')[:1], output_field=IntegerField()),
		following_count=Subquery(following_count_subquery.values('following_count')[:1], output_field=IntegerField())
	)

	context = {
		"members": members,
		"member": member,
		"heading": "Following",
	}
	return render(request, 'profile/follow.html', context)



@login_required
def follower_view(request, id=None):
	member = get_object_or_404(User, pk=id)
	followed_ids = Following.objects.filter(followed_id=id).values_list('follower_id', flat=True)
	members = User.objects.filter(id__in=followed_ids)
	
	followers_count_subquery = Following.objects.filter(followed=OuterRef('pk')).values('followed').annotate(followers_count=Count('follower'))
	following_count_subquery = Following.objects.filter(follower=OuterRef('pk')).values('follower').annotate(following_count=Count('followed'))
	
	members = members.annotate(
		followers_count=Subquery(followers_count_subquery.values('followers_count')[:1], output_field=IntegerField()),
		following_count=Subquery(following_count_subquery.values('following_count')[:1], output_field=IntegerField())
	)

	context = {
		"members": members,
		"member": member,
		"heading": "Followers",
	}
	return render(request, 'profile/follow.html', context)


@login_required
def follow_unfollow_view(request, id):
	if request.method == "POST":
		follower = request.user
		followed = get_object_or_404(User, id=id)
		try:
			following = Following.objects.get(follower=follower, followed=followed)
			following.delete()
			http = "<button type='submit' class='in-stock' id='{member_id}''>Follow</button>".format(member_id=id)
		except Following.DoesNotExist:
			Following.objects.create(follower=follower, followed=followed)
			http = "<button type='submit' class='out-of-stock' id='{member_id}''>Unfollow</button>".format(member_id=id)
	
	csrf_token = get_token(request)
	token_input = "<input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>".format(csrf_token=csrf_token)

	http = "<form method='POST' action='/accounts/follow_unfollow/{member_id}' hx-post='/accounts/follow_unfollow/{member_id}/' hx-swap='outerHTML'>".format(member_id=id) + token_input + http + "</form>"

	return HttpResponse(http)
