from decimal import Decimal
from django.utils import timezone
from .models import CreditDecision
from apps.scoring.models import ScoringResult


class CreditDecisionEngine:
    """
    Движок вынесения кредитных решений.
    Применяет кредитную политику банка на основе скоринговой оценки риска,
    параметров кредитного продукта и лимитов заемщика.
    """

    @classmethod
    def evaluate_automatic_decision(cls, application) -> CreditDecision:
        scoring = application.scoring_results.first()
        product = application.product
        company = application.company
        requested_amount = Decimal(str(application.requested_amount))
        term_months = application.term_months

        # Delete old decision if recalculating
        CreditDecision.objects.filter(application=application).delete()

        # 1. Стоп-факторы или критический риск -> Отказ
        if scoring.stop_factors or scoring.risk_level == ScoringResult.RiskLevel.CRITICAL:
            reasons = list(scoring.stop_factors) if scoring.stop_factors else [
                'Критический уровень совокупного кредитного риска заемщика.',
                'Недостаточный объем выручки для обслуживания запрашиваемой суммы.'
            ]
            rationale = (
                'К сожалению, в настоящее время банк не готов предоставить финансирование по данной заявке. '
                'Решение принято на основании данных государственных реестров и кредитной истории. '
                'Вы сможете подать повторную заявку после урегулирования замечаний через 30 календарных дней.'
            )
            return CreditDecision.objects.create(
                application=application,
                decision_type=CreditDecision.DecisionType.REJECTED,
                is_automated=True,
                approved_amount=Decimal('0.00'),
                approved_term_months=0,
                approved_rate=Decimal('0.00'),
                monthly_payment=Decimal('0.00'),
                rationale=rationale,
                rejection_reasons=reasons,
                client_response=CreditDecision.ClientResponse.PENDING,
            )

        # 2. Низкий риск и высокая надежность -> Автоматическое одобрение
        if scoring.recommendation == ScoringResult.Recommendation.AUTO_APPROVE:
            rate = product.base_rate
            # Бонус за отличный скоринг (>85 баллов)
            if scoring.score >= 85:
                rate = max(Decimal('11.00'), rate - Decimal('0.50'))

            monthly_pmt = product.calculate_estimated_payment(requested_amount, term_months)
            rationale = (
                f'Поздравляем! Ваша заявка одобрена автоматически на запрашиваемых условиях. '
                f'Сумма: {requested_amount:,.2f} руб., срок: {term_months} мес., ставка: {rate}% годовых. '
                f'Ознакомьтесь с индивидуальными условиями договора и подтвердите согласие.'
            )
            return CreditDecision.objects.create(
                application=application,
                decision_type=CreditDecision.DecisionType.APPROVED,
                is_automated=True,
                approved_amount=requested_amount,
                approved_term_months=term_months,
                approved_rate=rate,
                monthly_payment=monthly_pmt,
                rationale=rationale,
                rejection_reasons=[],
                client_response=CreditDecision.ClientResponse.PENDING,
            )

        # 3. Встречное предложение (Снижение суммы для безопасной долговой нагрузки)
        if scoring.recommendation == ScoringResult.Recommendation.COUNTER_OFFER:
            latest_fin = company.financial_reports.first()
            revenue = latest_fin.annual_revenue if latest_fin else Decimal('10000000.00')

            # Лимит: максимум 30% годовой выручки
            max_safe_amount = round(revenue * Decimal('0.30'), -4)
            counter_amount = min(requested_amount, max(Decimal('1000000.00'), max_safe_amount))
            counter_term = min(term_months, 24)
            counter_rate = product.base_rate + Decimal('1.50')
            monthly_pmt = product.calculate_estimated_payment(counter_amount, counter_term)

            rationale = (
                f'Банк готов предоставить финансирование на адаптированных условиях. '
                f'Сумма скорректирована с {requested_amount:,.0f} руб. до {counter_amount:,.0f} руб. '
                f'с целью сохранения комфортной долговой нагрузки вашего бизнеса (<30% от выручки).'
            )
            return CreditDecision.objects.create(
                application=application,
                decision_type=CreditDecision.DecisionType.COUNTER_OFFER,
                is_automated=True,
                approved_amount=counter_amount,
                approved_term_months=counter_term,
                approved_rate=counter_rate,
                monthly_payment=monthly_pmt,
                rationale=rationale,
                rejection_reasons=[],
                client_response=CreditDecision.ClientResponse.PENDING,
            )

        # 4. Ручное рассмотрение андеррайтером
        rationale = (
            'Заявка успешно прошла предварительный скоринг и направлена на индивидуальное рассмотрение '
            'кредитному эксперту Альфа-Банка. Мы уведомим вас о решении в ближайшее время.'
        )
        return CreditDecision.objects.create(
            application=application,
            decision_type=CreditDecision.DecisionType.MANUAL_REVIEW_REQUIRED,
            is_automated=True,
            approved_amount=Decimal('0.00'),
            approved_term_months=0,
            approved_rate=Decimal('0.00'),
            monthly_payment=Decimal('0.00'),
            rationale=rationale,
            rejection_reasons=[],
            client_response=CreditDecision.ClientResponse.PENDING,
        )

    @classmethod
    def apply_manual_decision(
        cls,
        application,
        officer_user,
        decision_type: str,
        approved_amount: Decimal = Decimal('0.00'),
        approved_term_months: int = 0,
        approved_rate: Decimal = Decimal('0.00'),
        notes: str = '',
        reasons: list = None
    ) -> CreditDecision:
        """Применение ручного решения сотрудником банка (андеррайтером)."""
        reasons = reasons or []
        product = application.product
        monthly_pmt = Decimal('0.00')

        if decision_type in (CreditDecision.DecisionType.APPROVED, CreditDecision.DecisionType.COUNTER_OFFER):
            monthly_pmt = product.calculate_estimated_payment(approved_amount, approved_term_months)
            if decision_type == CreditDecision.DecisionType.APPROVED:
                rationale = (
                    f'Заявка одобрена андеррайтером банка. '
                    f'Сумма: {approved_amount:,.2f} руб., срок: {approved_term_months} мес., ставка: {approved_rate}% годовых.'
                )
            else:
                rationale = (
                    f'Андеррайтер банка сформировал встречное предложение: '
                    f'Сумма: {approved_amount:,.2f} руб., срок: {approved_term_months} мес., ставка: {approved_rate}% годовых.'
                )
        elif decision_type == CreditDecision.DecisionType.ADDITIONAL_INFO_REQUIRED:
            rationale = (
                f'Для продолжения рассмотрения заявки банку требуются дополнительные сведения: {notes}'
            )
        else:
            rationale = (
                'По результатам экспертного рассмотрения заявки банком принято отрицательное решение.'
            )

        decision, _ = CreditDecision.objects.update_or_create(
            application=application,
            defaults={
                'decision_type': decision_type,
                'is_automated': False,
                'decided_by': officer_user,
                'approved_amount': approved_amount,
                'approved_term_months': approved_term_months,
                'approved_rate': approved_rate,
                'monthly_payment': monthly_pmt,
                'rationale': rationale,
                'rejection_reasons': reasons,
                'underwriter_notes': notes,
                'client_response': CreditDecision.ClientResponse.PENDING,
                'decided_at': timezone.now(),
            }
        )
        return decision
