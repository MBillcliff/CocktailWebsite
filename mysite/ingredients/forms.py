from django import forms
from .models import Ingredient


class IngredientForm(forms.ModelForm):
	required_css_field = 'required-field'
	name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
	description = forms.CharField(widget=forms.TextInput(attrs={"rows":2}))
	image_url = forms.CharField(required=False)

	class Meta:
		model=Ingredient
		fields = ['name', 'description', 'image_url',]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields:
			self.fields[str(field)].widget.attrs.update(
				placeholder=f'Ingredient {str(field)}')
