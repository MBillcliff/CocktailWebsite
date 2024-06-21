from django.db import models
from django.conf import settings
from django.urls import reverse
from string import capwords


class Ingredient(models.Model):
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)
	image_url = models.CharField(max_length=300)
	
	timestamp = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)

	users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="InStock", related_name="owned_by")

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("ingredients:detail", kwargs={"id":self.id})

	def save(self):
		self.name = capwords(self.name)
		super().save()


class InStock(models.Model):
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	
	in_stock = models.BooleanField(default=False)

	class Meta:
		unique_together = ('ingredient', 'user')