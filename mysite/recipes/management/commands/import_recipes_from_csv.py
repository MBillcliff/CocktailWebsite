import csv
from django.core.management.base import BaseCommand
from recipes.models import Recipe
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Import recipes from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            user = User.objects.get(pk=1)
            for row in reader:
                recipe = Recipe(
                    created_by=user,
                    name=row['name'],
                    description=row['description'],
                    directions=row['directions'],
                    glass=row['glass'],
                    image_url=row['image_url'],
                )
                recipe.save()
                
        self.stdout.write(self.style.SUCCESS('Recipes imported successfully.'))