import csv
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
from recipes.models import Recipe, IngredientQuantity
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        existing_ingredients = [obj.name for obj in Ingredient.objects.all()]
        existing_cocktails = [obj.name for obj in Recipe.objects.all()]
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            user = User.objects.get(pk=1)
            for row in reader:
                # Create Recipe Object Without Ingredients
                if row['Drink'] in existing_cocktails:
                    continue
                else:
                    existing_cocktails.append(row['Drink'])
                recipe = Recipe(
                    created_by=user,
                    name=row['Drink'],
                    description=row['Description'],
                    directions=row['Instructions'],
                    glass=row['Glass'],
                    image_url=row['DrinkThumb'],
                )
                recipe.save()           

                # Create Ingredient object for each ingredient
                for i in range(1, 16):
                    ing = row[f'Ingredient{i}']

                    if ing not in existing_ingredients and ing != '':
                        ingredient = Ingredient(
                            created_by=user,
                            name=ing,
                            description=ing,
                            # Set other fields accordingly
                        )
                        ingredient.save()
                        existing_ingredients.append(ing)
                    
                    if ing in existing_ingredients:
                        # Create ManyToMany field for the ingredient
                        ingredient = Ingredient.objects.get(name=ing)
                        ingredient_quantity = IngredientQuantity(
                            recipe = recipe,
                            ingredient=ingredient,
                            quantity = row[f'combined{i}'],
                            unit = row[f'unit{i}']
                        )
                        ingredient_quantity.save()
                        self.stdout.write(f'{recipe.name} - {ing}')
                    
        self.stdout.write(self.style.SUCCESS('Recipe and ingredients imported successfully.'))