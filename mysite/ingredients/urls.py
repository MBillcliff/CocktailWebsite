from django.urls import path

from .views import (
	ingredient_list_created_view,
	ingredient_create_view,
	ingredient_delete_view,
	ingredient_detail_view,
	ingredient_edit_view,
	ingredient_list_all_view,
	ingredient_change_stock_view,
	ingredient_home_view,
	ingredient_stock_view,
	)

app_name='ingredients'
urlpatterns=[
	path("", ingredient_home_view, name="home"),
	path("created/", ingredient_list_created_view, name="list_created"),	
	path("create/", ingredient_create_view, name="create"),
	path("<int:id>/", ingredient_detail_view, name="detail"),
	path("<int:id>/edit/", ingredient_edit_view, name="edit"),
	path("delete/<int:id>/", ingredient_delete_view, name="delete"),
	path("all/", ingredient_list_all_view, name="list_all"),
	path("change_stock/<int:id>/", ingredient_change_stock_view, name="change_stock"),
	path("stock/", ingredient_stock_view, name="stock")
]