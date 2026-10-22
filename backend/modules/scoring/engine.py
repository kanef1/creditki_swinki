from decimal import Decimal

def evaluate(company, financial, amount):
    factors = []
    def add(label, points):
        factors.append({'label': label, 'points': points})
    add('Возраст бизнеса', 20 if company.age_months >= 24 else 10 if company.age_months >= 12 else 0)
    margin = financial.profit / financial.revenue if financial.revenue else Decimal(0)
    add('Рентабельность', 20 if margin >= Decimal('.15') else 10 if margin > 0 else 0)
    burden = financial.debt / financial.revenue if financial.revenue else Decimal(99)
    add('Долговая нагрузка', 20 if burden <= Decimal('.3') else 10 if burden <= Decimal('.6') else 0)
    add('Кредитная история', 25 if company.credit_score >= 750 else 10 if company.credit_score >= 600 else 0)
    add('Сумма к годовой выручке', 15 if amount <= financial.revenue * Decimal('.3') else 5)
    stops = []
    if not company.active: stops.append('Компания не действует')
    if company.overdue_days > 60: stops.append('Просрочка более 60 дней')
    if company.tax_debt > Decimal('100000'): stops.append('Значительная налоговая задолженность')
    if financial.revenue <= 0: stops.append('Нет подтверждённой выручки')
    score = sum(f['points'] for f in factors)
    risk = 'HIGH' if stops or score < 50 else 'MEDIUM' if score < 80 else 'LOW'
    return dict(score=score, risk=risk, factors=factors, stops=stops,
                recommendation='REJECT' if stops or score < 50 else 'MANUAL' if score < 80 else 'APPROVE',
                explanation=f'Оценка {score} из 100. Использованы финансовые данные заявки и синтетические проверки. Модель rules-v1.')
