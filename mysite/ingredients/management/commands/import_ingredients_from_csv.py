import csv
from django.core.management.base import BaseCommand
from ingredients.models import Ingredient
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            user = User.objects.get(pk=1)
            for row in reader:
                ingredient = Ingredient(
                    created_by=user,
                    name=row['name'],
                    description=row['description'],
                    image_url=row['image_url'],
                    # Set other fields accordingly
                )
                ingredient.save()
                
        self.stdout.write(self.style.SUCCESS('Ingredients imported successfully.'))