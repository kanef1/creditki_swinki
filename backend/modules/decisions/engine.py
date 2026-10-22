from decimal import Decimal

def recommend(application, score):
    if score.stops or score.score < 50:
        return 'REJECTED', '; '.join(score.stops) or 'Финансовые показатели ниже порога модели', None
    if score.score < 80:
        return 'MANUAL_REVIEW', 'Требуется оценка финансовых показателей сотрудником', None
    limit = (application.financial.revenue * Decimal('.3')).quantize(Decimal('.01'))
    if application.amount > limit:
        if limit < application.product.min_amount:
            return 'MANUAL_REVIEW', 'Расчётный лимит ниже минимальной суммы продукта', None
        return 'OFFER_READY', 'Встречное предложение: сумма ограничена 30% выручки отчётного периода', limit
    return 'OFFER_READY', 'Устойчивые показатели, стоп-факторы отсутствуют', application.amount
