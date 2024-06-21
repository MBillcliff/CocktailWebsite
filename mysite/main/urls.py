from django.urls import include, path

from .views import home_view

urlpatterns = [
path("", home_view, name="home"),
path("recipes/", include('recipes.urls')),
path("ingredients/", include('ingredients.urls')),
path("accounts/", include('accounts.urls')),
path("search/", include('search.urls')),
path("home/", home_view, name="home"),
]
