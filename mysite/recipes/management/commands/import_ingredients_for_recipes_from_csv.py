import csv
from django.core.management.base import BaseCommand
from recipes.models import Recipe, IngredientQuantity
from ingredients.models import Ingredient
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Import recipes from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe = Recipe.objects.get(name=row['recipe_name'])
                ingredient = Ingredient.objects.get(name=row['ingredient_name'])
                ingredient_quantity = IngredientQuantity(
                    recipe = recipe,
                    ingredient=ingredient,
                    quantity = row['quantity'],
                    unit = row['unit'],
                )
                ingredient_quantity.save()
                
        self.stdout.write(self.style.SUCCESS('Recipe ingredients imported successfully.'))