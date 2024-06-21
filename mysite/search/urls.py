from django.urls import path

from.views import (
    search_all_view,
    search_recipe_view,
    search_ingredient_view,
    search_member_view,
)

app_name="search"
urlpatterns=[
    path("", search_all_view, name="search-initial"),
    path("<str:searched>/", search_all_view, name="search-all"),
    path("recipes/<str:searched>/", search_recipe_view, name="search-recipes"),
    path("ingredients/<str:searched>/", search_ingredient_view, name="search-ingredient"),
    path("members/<str:searched>/", search_member_view, name="search-memebers"),

]