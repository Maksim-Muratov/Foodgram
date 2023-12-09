import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def delete_existing_ingredients(self):
    """Удаление существующих ингредиентов."""
    Ingredient.objects.all().delete()
    self.stdout.write('- Существующие ингредиенты были удалены.')


class Command(BaseCommand):
    """Загружает ингредиенты из CSV файла."""

    def add_arguments(self, parser):
        """
        Добавляет команде аргумент для удаления существующих ингредиентов.
        """
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            dest='delete_existing',
            default=False,
            help='Удаляет существующие ингредиенты',
        )

    def handle(self, *args, **options):
        """Загрузка ингредиентов."""

        if options['delete_existing']:
            delete_existing_ingredients(self)

        records = []
        with open(
            './data/ingredients.csv', encoding='utf-8', newline=''
        ) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                record = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                records.append(record)

        Ingredient.objects.bulk_create(records)
        self.stdout.write('- Ингредиенты добавлены.')
