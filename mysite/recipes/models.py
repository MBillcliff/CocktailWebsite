from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from .validators import validate_unit_of_measure
from .utils import number_str_to_float
from string import capwords
from ingredients.models import Ingredient
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Recipe(models.Model):
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	name = models.CharField(max_length=220)
	description = models.TextField(blank=True, null=True)
	directions = models.TextField(blank=True, null=True) 
	glass = models.CharField(max_length=50, blank=True, null=True)
	image_url = models.CharField(max_length=300, blank=True, null=True, default="")

	timestamp = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)

	ingredients = models.ManyToManyField(Ingredient, through="IngredientQuantity", related_name="quantities")
	
	def __str__(self):
		return capwords(self.name)

	def get_absolute_url(self):
		return reverse("recipes:detail", kwargs={"id":self.id})

	def save(self, *args, **kwargs):
		self.name = capwords(self.name)
		self.glass = capwords(self.glass)
		if self.image_url is None:
			print("no image url")
			self.image_url = "https://i.imgur.com/SS8IRAQ.jpg"
		super().save(*args, **kwargs)


class IngredientQuantity(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

	unit = models.CharField(max_length=50, validators=[validate_unit_of_measure])
	quantity = models.CharField(max_length=50)
	quantity_as_float = models.FloatField(blank=True, null=True)

	class Meta:
		unique_together = ('recipe', 'ingredient')

	def save(self, *args, **kwargs):
		qty = self.quantity
		qty_as_float, qty_as_float_success = number_str_to_float(qty)
		if qty_as_float_success:
			self.quantity_as_float = qty_as_float
		else:
			self.quantity_as_float = None
		self.unit = self.unit.lower()
		try:
			super().save(*args, **kwargs)
		except IntegrityError:
			print("duplicates are not allowed")
		

class LikedRecipe(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	class Meta:
		unique_together = ('recipe', 'user')

class FavouriteRecipe(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	class Meta:
		unique_together = ('recipe', 'user')


class MadeRecipe(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	class Meta:
		unique_together = ('recipe', 'user')


class RecipeRating(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	class Meta:
		unique_together = ('recipe', 'user')
	rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )