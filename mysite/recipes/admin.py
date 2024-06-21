from django.contrib import admin
from django.contrib.auth import get_user_model

# Register your models here.
from .models import Recipe, IngredientQuantity, LikedRecipe, FavouriteRecipe, RecipeRating, MadeRecipe

User = get_user_model()

class RecipeIngredientInline(admin.StackedInline):
	model = IngredientQuantity
	extra = 0
	readonly_fields = ['quantity_as_float']

class RecipeAdmin(admin.ModelAdmin):
	inlines = [RecipeIngredientInline]
	list_display = ['name', 'created_by']
	raw_id_fields = ['created_by']

class LikeAdmin(admin.StackedInline):
	model = LikedRecipe

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientQuantity)
admin.site.register(LikedRecipe)