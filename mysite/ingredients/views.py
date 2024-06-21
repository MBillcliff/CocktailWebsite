from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import IngredientForm
from .models import Ingredient, InStock
from django.http import HttpResponse
from django.middleware.csrf import get_token


# Create your views here.
@login_required
def ingredient_stock_view(request):
	user_stock = [Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]
	user_stock = sorted(stock, key= lambda x: x.name)
	message="Your Stock"

	context = {
		"object": user_stock,
		"in_stock": user_stock,
		"message": message,
	}
	return render(request, "ingredients/list.html", context)

@login_required
def ingredient_list_created_view(request):
	qs = Ingredient.objects.filter(created_by=request.user).order_by('name')
	in_stock=[Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]
	message='Created'

	context = {
		"object":qs,
		"in_stock":in_stock,
		"message":message
	}
	return render(request, "ingredients/list.html", context)


@login_required
def ingredient_list_all_view(request):
	qs = Ingredient.objects.all().order_by('name')
	in_stock=[Ingredient.objects.get(pk=i.ingredient_id) for i in InStock.objects.filter(user=request.user) if i.in_stock]
	current_user = request.user
	current_path = request.path
	message='All'

	context = {
		"object":qs,
		"current_user":current_user,
		"in_stock":in_stock,
		"message":message,
		"current_path":current_path,
	}
	return render(request, "ingredients/list.html", context)


@login_required
def ingredient_delete_view(request, id):
	recipe = Ingredient.objects.get(pk=id)
	recipe.delete()
	return redirect(request.META.get('HTTP_REFERER'))


@login_required
def ingredient_detail_view(request, id=None):
	obj = get_object_or_404(Ingredient, id=id, created_by=request.user)
	context = {
		"object":obj
	}
	return render(request, "ingredients/detail.html", context)


@login_required
def ingredient_create_view(request):
	form = IngredientForm(request.POST or None)
	message="Create"

	if form.is_valid():
		new_form = form.save(commit=False)
		new_form.created_by_id = request.user.id
		new_form.save()
		return redirect("/ingredients/")

	context = {
		"form":form,
		"message":message
		}

	return render(request, "ingredients/create-update.html", context)


@login_required
def ingredient_edit_view(request, id=id):
	obj=get_object_or_404(Ingredient, id=id, created_by=request.user)
	form = IngredientForm(request.POST or None, instance=obj)
	message="Edit"

	if form.is_valid():
		new_form = form.save(commit=False)
		new_form.created_by_id = request.user.id
		new_form.save()
		return redirect("/ingredients/")

	context = {
		"form":form,
		"message":message
		}

	return render(request, "ingredients/create-update.html", context)


@login_required
def ingredient_change_stock_view(request, id):
	if request.method == 'POST':
        # Perform the logic to add the ingredient to the user's stock
		ingredient = get_object_or_404(Ingredient, pk=id)
		in_stock_obj, created = InStock.objects.get_or_create(ingredient=ingredient, user=request.user)
		in_stock_obj.in_stock = not in_stock_obj.in_stock
		in_stock_obj.save()

	ingredient_id = id

	if in_stock_obj.in_stock:
		http = "<button type='submit' class='in-stock' id='{ingredient_id}'>✔️</button>".format(ingredient_id=ingredient_id)
	else:
		http = "<button type='submit' class='out-of-stock' id='{ingredient_id}'>✖️</button>".format(ingredient_id=ingredient_id)

	csrf_token = get_token(request)
	token_input = "<input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>".format(csrf_token=csrf_token)

	http = "<form method='POST' action='/ingredients/change_stock/{ingredient_id}/' hx-post='/ingredients/change_stock/{ingredient_id}/' hx-swap='outerHTML'>".format(ingredient_id=ingredient_id) + token_input + http + "</form>"

	return HttpResponse(http)


def ingredient_home_view(request):
	return render(request, "ingredients/home.html")

