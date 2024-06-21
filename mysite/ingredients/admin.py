from django.contrib import admin
from django.contrib.auth import get_user_model

# Register your models here.
from .models import Ingredient, InStock

User = get_user_model()

class IngredientAdmin(admin.ModelAdmin):
	list_display = ['name', 'created_by']
	raw_id_fields = ['created_by']

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(InStock)
