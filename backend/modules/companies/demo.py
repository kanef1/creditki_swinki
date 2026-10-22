from decimal import Decimal
from uuid import uuid4, uuid5, NAMESPACE_URL
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Company, CompanyMembership, DemoCompany

PROFILES = [
    dict(code='approve',title='Автоматическое одобрение',name='ООО «Вектор роста»',age_months=54,credit_score=820,tax_debt='0.00',overdue_days=0,revenue='58000000.00',profit='12400000.00',debt='1000000.00',amount='5000000.00',term=24,purpose='Закупка оборудования для расширения производства',expected_status='OFFER_READY',expected_amount='5000000.00',description='Зрелый бизнес с высокой рентабельностью, хорошей кредитной историей и небольшой долговой нагрузкой.',expected='Предложение на всю запрошенную сумму — 5 млн ₽.'),
    dict(code='counter',title='Встречное предложение',name='ИП Смирнов Алексей',age_months=36,credit_score=780,tax_debt='0.00',overdue_days=0,revenue='15000000.00',profit='2700000.00',debt='3000000.00',amount='5000000.00',term=24,purpose='Пополнение оборотных средств перед новым сезоном',expected_status='OFFER_READY',expected_amount='4500000.00',description='Устойчивые показатели, но запрошенная сумма превышает 30% годовой выручки.',expected='Встречная сумма 4,5 млн ₽ вместо запрошенных 5 млн ₽.'),
    dict(code='manual',title='Ручное рассмотрение',name='ООО «Технопром»',age_months=18,credit_score=680,tax_debt='48000.00',overdue_days=0,revenue='24000000.00',profit='1900000.00',debt='9000000.00',amount='4000000.00',term=36,purpose='Модернизация производственной линии',expected_status='MANUAL_REVIEW',expected_amount=None,description='Молодой бизнес, умеренный балл БКИ, невысокая рентабельность и заметная долговая нагрузка.',expected='Заявка передаётся сотруднику для обоснованного решения.'),
    dict(code='reject',title='Отказ со стоп-факторами',name='ООО «Стройгрупп Риск»',age_months=3,credit_score=415,tax_debt='110000.00',overdue_days=15,revenue='650000.00',profit='-120000.00',debt='800000.00',amount='300000.00',term=18,purpose='Пополнение оборотных средств строительной бригады',expected_status='REJECTED',expected_amount=None,description='За первые 3 месяца выручка 650 тыс. ₽, убыток 120 тыс. ₽. Просрочка 15 дней и налоговый долг 110 тыс. ₽.',expected='Отказ из-за налоговой задолженности и слабых финансовых показателей.'),
]

def profile_for(code):
    profile=next((p for p in PROFILES if p['code']==code),None)
    if not profile: raise ValidationError('Неизвестный демонстрационный сценарий')
    return profile

@transaction.atomic
def ensure_workspace(user):
    # Serialize bootstraps and scenario runs for this visitor, never share company rows.
    get_user_model().objects.select_for_update().get(pk=user.pk)
    from modules.products.models import CreditProduct
    product=CreditProduct.objects.order_by('id').first()
    for profile in PROFILES:
        entry=DemoCompany.objects.filter(user=user,code=profile['code']).select_related('company').first()
        if entry is None:
            company=Company.objects.create(name=profile['name'],inn=f'99{uuid4().int % 10**10:010d}',age_months=profile['age_months'],credit_score=profile['credit_score'],tax_debt=profile['tax_debt'],overdue_days=profile['overdue_days'])
            CompanyMembership.objects.create(user=user,company=company)
            entry=DemoCompany.objects.create(user=user,company=company,code=profile['code'])
        else:
            # Refresh only managed demo metadata; submitted application financials remain historical.
            fields=['age_months','credit_score','tax_debt','overdue_days']
            Company.objects.filter(pk=entry.company_id).update(**{field:profile[field] for field in fields})
        if product:
            create_scenario(user,entry,profile,uuid5(NAMESPACE_URL,f'credit-sample:{user.pk}:{profile["code"]}'),product)

def create_scenario(user,entry,profile,key,product):
    from modules.applications.models import Application, FinancialData, StatusHistory
    from modules.applications.services import submit
    existing=Application.objects.filter(created_by=user,creation_key=key).first()
    if existing:
        if existing.company_id!=entry.company_id: raise ValidationError('Ключ запроса уже использован для другой компании')
        return existing
    amount=Decimal(profile['amount']);term=profile['term']
    if not product.min_amount<=amount<=product.max_amount or not product.min_term<=term<=product.max_term:
        raise ValidationError('Демо-параметры не соответствуют продукту; восстановите синтетический каталог')
    app=Application.objects.create(company=entry.company,product=product,created_by=user,creation_key=key,amount=amount,term=term,purpose=profile['purpose'])
    FinancialData.objects.create(application=app,**{field:Decimal(profile[field]) for field in ['revenue','profit','debt']})
    StatusHistory.objects.create(application=app,status='DRAFT',actor=user,reason='Синтетическая заявка сценария для жюри')
    return submit(app.pk,user)

def catalog(user):
    entries={entry.code:entry for entry in DemoCompany.objects.filter(user=user).select_related('company')}
    from modules.products.models import CreditProduct
    product=CreditProduct.objects.order_by('id').first()
    return [{**p,'period_months':min(p['age_months'],12),'company':entries[p['code']].company_id,'inn':entries[p['code']].company.inn,'product':product.pk if product else None,'rate':str(product.rate) if product else None} for p in PROFILES if p['code'] in entries]
