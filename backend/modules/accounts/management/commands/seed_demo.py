import os
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from modules.companies.models import Company, CompanyMembership
from modules.products.models import CreditProduct
from modules.applications.models import Application, FinancialData, StatusHistory
from modules.applications.services import submit

class Command(BaseCommand):
    help = 'Create synthetic demo data; --reset deletes demo applications only'
    def add_arguments(self, parser): parser.add_argument('--reset',action='store_true')
    @transaction.atomic
    def handle(self,*args,**options):
        password = os.getenv('DEMO_PASSWORD')
        if not password: raise CommandError('Set DEMO_PASSWORD to seed demo accounts')
        User = get_user_model()
        bank, _ = User.objects.get_or_create(username='bank')
        bank.is_staff = True; bank.set_password(password); bank.save()
        for name, description, maximum, term, rate in [('Оборотные средства','Для закупки товаров и текущих расходов',5000000,36,'19.50'),('Развитие бизнеса','Откройте новое направление или торговую точку',15000000,60,'20.00'),('Оборудование','Обновите производственные мощности',10000000,48,'18.00')]:
            CreditProduct.objects.update_or_create(name=name,defaults=dict(description=description,min_amount=100000,max_amount=maximum,min_term=6,max_term=term,rate=rate))
        product = CreditProduct.objects.order_by('id').first()
        profiles = [('demo_a','ООО «Северный свет»','9900000001',48,850,0,True,12000000,2400000,1000000,1000000),('demo_b','ООО «Новая линия»','9900000002',36,800,0,True,6000000,1200000,500000,3000000),('demo_c','ООО «Точка роста»','9900000003',15,680,0,True,8000000,640000,3000000,1000000),('demo_d','ООО «Контур»','9900000004',36,500,95,True,5000000,100000,4000000,1000000)]
        for username,name,inn,age,score,overdue,active,revenue,profit,debt,amount in profiles:
            user,_=User.objects.get_or_create(username=username)
            user.set_password(password); user.save()
            company,_=Company.objects.update_or_create(inn=inn,defaults=dict(name=name,age_months=age,credit_score=score,overdue_days=overdue,active=active))
            CompanyMembership.objects.get_or_create(user=user,company=company)
            if options['reset']: Application.objects.filter(company=company).delete()
            if not Application.objects.filter(company=company).exists():
                app=Application.objects.create(company=company,product=product,created_by=user,amount=Decimal(amount),term=24,purpose='Закупка оборудования и расширение бизнеса')
                FinancialData.objects.create(application=app,revenue=Decimal(revenue),profit=Decimal(profit),debt=Decimal(debt))
                StatusHistory.objects.create(application=app,status='DRAFT',actor=user,reason='Создан демонстрационный черновик')
                submit(app.pk,user)
        self.stdout.write('Synthetic accounts: demo_a, demo_b, demo_c, demo_d, bank. Password from DEMO_PASSWORD.')
