import json
import pathlib

from django.core.management.base import BaseCommand, CommandParser
from django.db import IntegrityError

from recipes.models import Ingredient, MeasureUnit


class Command(BaseCommand):
    """
    Импортирует данные из json-объекта в модель Ingredient,
    а также создаёт объекты в MeasureUnit и связывает их.
    При обнаружении дубликата/некорректной записи(нет необходимых полей),
    игнорирует конкретную запись и продолжает импорт дальше, печатая ошибку.
    """
    help = 'Импортирует в проект данные из json-объекта в модель Ingredient.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('table_name', nargs=1, type=pathlib.Path)

    def handle(self, *args, **options):
        """Сами действия при запуске команды."""
        table_name = options['table_name'][0]
        self.stdout.write(self.style.NOTICE('Импорт начался, ожидайте...'))
        self.stdout.write(self.style.NOTICE('============================='))
        with open(table_name,
                  newline='',
                  encoding='utf-8') as file:
            reader = json.load(file)
            total_rows = 0
            success = 0

            for row in reader:
                total_rows += 1

                try:
                    unit, _ = MeasureUnit.objects.get_or_create(
                        name=row['measurement_unit'])
                    Ingredient.objects.get_or_create(
                        name=row['name'], measurement_unit=unit)
                    success += 1

                except IntegrityError as err:
                    print(f'Error: {err.args}')
                    continue
        errors = total_rows - success
        self.stdout.write(self.style.SUCCESS(
            f'\nДанные из таблицы {table_name} '
            f'успешно импортированы в модель {Ingredient.__name__}!'
            f'\nКоличество ошибок: {errors}'))
