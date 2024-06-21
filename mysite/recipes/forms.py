from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Recipe, IngredientQuantity
from ingredients.models import Ingredient
from django.core.validators import MaxLengthValidator


class RecipeForm(forms.ModelForm):
    required_css_class = 'required-field'
    name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Cocktail Name"}),
        validators=[MaxLengthValidator(30)]
    )
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Cocktail Description"}))
    directions = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Cocktail Directions"}))
    glass = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Glass Type"}))
    image_url = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Image URL (optional)"}))

    class Meta:
        model = Recipe
        fields = ['name', 'description', 'directions', 'glass', 'image_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })


class RecipeIngredientForm(forms.ModelForm):
    required_css_class = 'required-field'
    quantity = forms.CharField(widget=forms.TextInput(attrs={'class': 'ingredient-field'}))
    unit = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'ingredient-field'}))

    class Meta:
        model = IngredientQuantity
        fields = ['ingredient', 'quantity', 'unit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = self.fields['ingredient'].queryset.order_by('name')
        for field in self.fields:
            self.fields[str(field)].widget.attrs.update({
                'placeholder': f'{str(field).capitalize()}',
                'class': 'ingredient-field'
            })