from django.core.management.base import BaseCommand
from modules.products.models import CreditProduct


class Command(BaseCommand):
    help='Create the public synthetic catalog without shared customer or bank accounts'

    def handle(self,*args,**options):
        for name,description,maximum,term,rate in [
            ('Оборотные средства','Для закупки товаров и текущих расходов',5000000,36,'19.50'),
            ('Развитие бизнеса','Откройте новое направление или торговую точку',15000000,60,'20.00'),
            ('Оборудование','Обновите производственные мощности',10000000,48,'18.00'),
        ]:
            CreditProduct.objects.update_or_create(name=name,defaults=dict(description=description,min_amount=100000,max_amount=maximum,min_term=6,max_term=term,rate=rate))
        self.stdout.write('Public synthetic catalog ready; no shared logins created.')
