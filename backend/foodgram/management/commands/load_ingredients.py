import json
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON файла'

    def handle(self, *args, **options):
        with open(
            'data/ingredients.json',
            'r',
            encoding='utf-8'
        ) as f:
            ingredients = json.load(f)

        created_count = 0
        for item in ingredients:
            _, created = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно загружено {created_count} ингредиентов'
            )
        )
