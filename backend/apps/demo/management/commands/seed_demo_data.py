from django.core.management.base import BaseCommand
from apps.demo.services import DemoDataSeeder


class Command(BaseCommand):
    help = 'Заполняет базу данных демонстрационными компаниями, продуктами и сценариями.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Запуск генерации демонстрационных данных Альфа-Банка...'))
        result = DemoDataSeeder.seed_all()
        self.stdout.write(self.style.SUCCESS(
            f"Успешно созданы пользователи: {', '.join(result['users'])}\n"
            f"Успешно созданы и обработаны заявки: {', '.join(result['applications'])}"
        ))
