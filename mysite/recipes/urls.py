from django.urls import path

from .views import (
	recipe_list_created_view,
	recipe_list_all_view, 
	recipe_detail_view,
	recipe_create_view,
	recipe_update_view,
	delete_ingredient_view,
	delete_recipe_view,
	recipe_home_view,
	recipe_can_make_view,
    recipe_filter_by_ingredient_view,
    like_recipe_view,
    favourite_recipe_view,
    made_recipe_view,
    rate_recipe_view,
	)

app_name='recipes'
urlpatterns=[
	path("", recipe_home_view, name="home"),
	path("created/", recipe_list_created_view, name="list_created"),
	path("all/", recipe_list_all_view, name="list_all"),
	path("create/", recipe_create_view, name="create"),
	path("<int:id>/edit/", recipe_update_view, name="update"),
	path("<int:id>/", recipe_detail_view, name="detail"),
	path("delete_ingredient/<int:id>", delete_ingredient_view, name="delete_ingredient"),
	path("delete_recipe/<int:id>", delete_recipe_view, name="delete_recipe"),
    path("delete_recipe/", delete_recipe_view, name="delete_empty_recipe"),
	path("can_make/", recipe_can_make_view, name="can_make"),
    path("filter_by/<int:ingredient_id>/", recipe_filter_by_ingredient_view, name="filter_by_ingredient"),
    path("like/<int:id>/", like_recipe_view, name="like"),
    path("favourite/<int:id>/", favourite_recipe_view, name="favourite"),
    path("made/<int:id>/", made_recipe_view, name="made"),
    path("rate/<int:id>/<int:rating>/", rate_recipe_view, name="rate"),
    
]