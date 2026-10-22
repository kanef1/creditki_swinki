from decimal import Decimal
from .models import ScoringResult
from apps.verification.models import VerificationResult


class RuleBasedScoringEngine:
    """
    Прозрачный детерминированный движок скоринга кредитного риска бизнеса.
    Формирует скоринговый балл (0-100), список влияющих факторов, уровень риска
    и перечень сработавших стоп-факторов на основе финансовых показателей заемщика
    и данных верификации (ФНС, БКИ, ЕГРЮЛ).
    """

    @classmethod
    def evaluate(cls, application) -> ScoringResult:
        company = application.company
        product = application.product
        requested_amount = Decimal(str(application.requested_amount))
        term_months = application.term_months

        # Financial data
        latest_fin = company.financial_reports.first()
        revenue = latest_fin.annual_revenue if latest_fin else Decimal('0.00')
        net_profit = latest_fin.net_profit if latest_fin else Decimal('0.00')
        existing_debt = latest_fin.total_debt if latest_fin else Decimal('0.00')
        existing_monthly_pmt = latest_fin.monthly_credit_payments if latest_fin else Decimal('0.00')

        # External verification data
        verifications = application.verification_results.all()
        fns_res = next((v for v in verifications if v.source == VerificationResult.Source.FNS), None)
        bki_res = next((v for v in verifications if v.source == VerificationResult.Source.BKI), None)
        egrul_res = next((v for v in verifications if v.source == VerificationResult.Source.EGRUL), None)

        score = 50  # Базовая медианная оценка
        factors = []
        stop_factors = []

        # -------------------------------------------------------------
        # 1. Возраст бизнеса (Регистрация)
        # -------------------------------------------------------------
        business_age = company.business_age_years
        if business_age < 0.5:
            delta = -20
            score += delta
            factors.append({
                'category': 'Регистрация',
                'name': 'Срок деятельности менее 6 месяцев',
                'impact': delta,
                'type': 'NEGATIVE',
                'description': f'Возраст бизнеса {business_age} г. Высокая уязвимость на ранней стадии.'
            })
            stop_factors.append('Срок деятельности бизнеса менее минимального порога 6 месяцев.')
        elif business_age < 1.0:
            delta = -5
            score += delta
            factors.append({
                'category': 'Регистрация',
                'name': 'Срок деятельности до 1 года',
                'impact': delta,
                'type': 'NEUTRAL',
                'description': f'Возраст компании {business_age} г. Требуется подтверждение стабильности.'
            })
        elif business_age < 3.0:
            delta = 10
            score += delta
            factors.append({
                'category': 'Регистрация',
                'name': 'Зрелый бизнес от 1 до 3 лет',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': f'Компания устойчиво функционирует на рынке {business_age} года.'
            })
        else:
            delta = 15
            score += delta
            factors.append({
                'category': 'Регистрация',
                'name': 'Стабильный бизнес более 3 лет',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': f'Компания успешно работает {business_age} лет.'
            })

        # -------------------------------------------------------------
        # 2. Финансовые результаты (Прибыльность)
        # -------------------------------------------------------------
        if net_profit <= 0:
            delta = -25
            score += delta
            factors.append({
                'category': 'Финансы',
                'name': 'Убыточная деятельность компании',
                'impact': delta,
                'type': 'NEGATIVE',
                'description': f'Чистый финансовый результат отрицательный: {net_profit:,.0f} руб.'
            })
            if net_profit < Decimal('-1000000'):
                stop_factors.append('Существенный чистый убыток компании по итогам отчетного периода.')
        else:
            profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
            if profit_margin >= 10:
                delta = 15
                score += delta
                factors.append({
                    'category': 'Финансы',
                    'name': 'Высокая рентабельность бизнеса',
                    'impact': f'+{delta}',
                    'type': 'POSITIVE',
                    'description': f'Рентабельность по чистой прибыли {profit_margin:.1f}% ({net_profit:,.0f} руб).'
                })
            else:
                delta = 5
                score += delta
                factors.append({
                    'category': 'Финансы',
                    'name': 'Положительная чистая прибыль',
                    'impact': f'+{delta}',
                    'type': 'POSITIVE',
                    'description': f'Чистая прибыль {net_profit:,.0f} руб, рентабельность {profit_margin:.1f}%.'
                })

        # -------------------------------------------------------------
        # 3. Соотношение суммы кредита и выручки
        # -------------------------------------------------------------
        loan_to_revenue = (requested_amount / revenue * 100) if revenue > 0 else 100
        if loan_to_revenue <= 10:
            delta = 15
            score += delta
            factors.append({
                'category': 'Сумма заявки',
                'name': 'Низкая долговая нагрузка от кредита',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': f'Запрашиваемая сумма составляет всего {loan_to_revenue:.1f}% от годовой выручки.'
            })
        elif loan_to_revenue <= 25:
            delta = 10
            score += delta
            factors.append({
                'category': 'Сумма заявки',
                'name': 'Умеренная доля кредита в выручке',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': f'Запрос {requested_amount:,.0f} руб ({loan_to_revenue:.1f}% годового оборота).'
            })
        elif loan_to_revenue <= 40:
            factors.append({
                'category': 'Сумма заявки',
                'name': 'Повышенная доля кредита в выручке',
                'impact': 0,
                'type': 'NEUTRAL',
                'description': f'Запрашиваемый объем финансирования составляет {loan_to_revenue:.1f}% от выручки.'
            })
        else:
            delta = -20
            score += delta
            factors.append({
                'category': 'Сумма заявки',
                'name': 'Высокая запрашиваемая сумма относительно оборота',
                'impact': delta,
                'type': 'NEGATIVE',
                'description': f'Запрос {requested_amount:,.0f} руб превышает 40% годовой выручки ({loan_to_revenue:.1f}%).'
            })

        # -------------------------------------------------------------
        # 4. Долговая нагрузка (DSTI)
        # -------------------------------------------------------------
        estimated_monthly_payment = product.calculate_estimated_payment(requested_amount, term_months)
        monthly_revenue = (revenue / 12) if revenue > 0 else Decimal('1.00')
        total_monthly_obligations = existing_monthly_pmt + estimated_monthly_payment
        dsti_ratio = (total_monthly_obligations / monthly_revenue * 100)

        if dsti_ratio <= 20:
            delta = 15
            score += delta
            factors.append({
                'category': 'Платежеспособность',
                'name': 'Комфортный коэффициент долговой нагрузки (DSTI)',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': f'Общий платеж по кредитам составляет {dsti_ratio:.1f}% от среднемесячной выручки.'
            })
        elif dsti_ratio <= 35:
            delta = 5
            score += delta
            factors.append({
                'category': 'Платежеспособность',
                'name': 'Приемлемый уровень долговой нагрузки',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': f'Платежи по обязательствам составляют {dsti_ratio:.1f}% от среднемесячного оборота.'
            })
        elif dsti_ratio <= 50:
            delta = -10
            score += delta
            factors.append({
                'category': 'Платежеспособность',
                'name': 'Повышенная долговая нагрузка',
                'impact': delta,
                'type': 'NEGATIVE',
                'description': f'Платежи {total_monthly_obligations:,.0f} руб/мес ({dsti_ratio:.1f}% от среднемесячной выручки).'
            })
        else:
            delta = -25
            score += delta
            factors.append({
                'category': 'Платежеспособность',
                'name': 'Критическая долговая нагрузка',
                'impact': delta,
                'type': 'NEGATIVE',
                'description': f'Платежи превышают 50% среднемесячного дохода ({dsti_ratio:.1f}%).'
            })

        # -------------------------------------------------------------
        # 5. ФНС и налоговая дисциплина
        # -------------------------------------------------------------
        if fns_res and fns_res.stop_factor_raised:
            delta = -35
            score += delta
            factors.append({
                'category': 'Налоги и ФНС',
                'name': 'Действующая налоговая задолженность / Блокировка счетов',
                'impact': delta,
                'type': 'NEGATIVE',
                'description': fns_res.summary
            })
            stop_factors.append('Наличие действующей задолженности перед бюджетом по данным ФНС.')
        else:
            delta = 10
            score += delta
            factors.append({
                'category': 'Налоги и ФНС',
                'name': 'Идеальная налоговая дисциплина',
                'impact': f'+{delta}',
                'type': 'POSITIVE',
                'description': 'Задолженности перед бюджетом отсутствуют, блокировок счетов нет.'
            })

        # -------------------------------------------------------------
        # 6. Кредитная история (БКИ)
        # -------------------------------------------------------------
        if bki_res:
            bki_score = bki_res.details.get('bki_score', 700)
            max_overdue = bki_res.details.get('max_past_overdue_days', 0)
            current_overdue = bki_res.details.get('current_overdue_rub', 0)

            if current_overdue > 0 or max_overdue >= 90:
                delta = -40
                score += delta
                factors.append({
                    'category': 'Кредитная история',
                    'name': 'Открытые или длительные просрочки (>90 дней)',
                    'impact': delta,
                    'type': 'NEGATIVE',
                    'description': f'Обнаружена просроченная задолженность {current_overdue:,.0f} руб.'
                })
                stop_factors.append('Наличие просроченной кредитной задолженности свыше 90 дней по данным БКИ.')
            elif max_overdue > 0:
                delta = -10
                score += delta
                factors.append({
                    'category': 'Кредитная история',
                    'name': 'Погашенные исторические задержки платежей',
                    'impact': delta,
                    'type': 'NEGATIVE',
                    'description': f'Имелись факты просрочек до {max_overdue} дней в прошлых периодах.'
                })
            else:
                delta = 15
                score += delta
                factors.append({
                    'category': 'Кредитная история',
                    'name': 'Безупречная кредитная история заемщика',
                    'impact': f'+{delta}',
                    'type': 'POSITIVE',
                    'description': f'Рейтинг БКИ {bki_score}/850. Просрочек платежей не зафиксировано.'
                })

        # -------------------------------------------------------------
        # Финализация балла и классификация риска
        # -------------------------------------------------------------
        score = max(0, min(100, score))

        has_bki_warning = bki_res and (bki_res.status == VerificationResult.Status.WARNING or bki_res.risk_flag_raised)
        young_business_large_loan = business_age < 1.5 and requested_amount >= Decimal('4000000.00')

        if stop_factors or score < 40:
            risk_level = ScoringResult.RiskLevel.CRITICAL if stop_factors else ScoringResult.RiskLevel.HIGH
            recommendation = ScoringResult.Recommendation.REJECT
            explanation = (
                f'Оценка риска: {score}/100. Обнаружены стоп-факторы или критический уровень риска. '
                'Автоматическое или стандартное кредитование невозможно.'
            )
        elif has_bki_warning or young_business_large_loan:
            risk_level = ScoringResult.RiskLevel.MEDIUM
            recommendation = ScoringResult.Recommendation.MANUAL_REVIEW
            reasons_list = []
            if has_bki_warning:
                reasons_list.append('зафиксированы исторические задержки платежей в БКИ')
            if young_business_large_loan:
                reasons_list.append(f'запрошена крупная сумма ({requested_amount:,.0f} руб) для молодого бизнеса ({business_age} г.)')
            explanation = (
                f'Оценка риска: {score}/100 (Умеренный риск). '
                f'Заявка не подлежит сквозному автоматическому одобрению, так как {", ".join(reasons_list)}. '
                'Требуется ручная верификация андеррайтером банка.'
            )
        elif score >= 75:
            # Check if loan amount requires counter-offer due to leverage
            if loan_to_revenue > 30:
                risk_level = ScoringResult.RiskLevel.MEDIUM
                recommendation = ScoringResult.Recommendation.COUNTER_OFFER
                explanation = (
                    f'Оценка риска: {score}/100 (Низкий риск). Заемщик финансово устойчив, '
                    f'однако запрашиваемая сумма ({requested_amount:,.0f} руб) превышает комфортную нагрузку.'
                )
            else:
                risk_level = ScoringResult.RiskLevel.LOW
                recommendation = ScoringResult.Recommendation.AUTO_APPROVE
                explanation = (
                    f'Оценка риска: {score}/100 (Низкий кредитный риск). Высокая финансовая устойчивость, '
                    'отличная платежная дисциплина и соответствие параметрам кредитного продукта.'
                )
        elif score >= 50:
            risk_level = ScoringResult.RiskLevel.MEDIUM
            recommendation = ScoringResult.Recommendation.MANUAL_REVIEW
            explanation = (
                f'Оценка риска: {score}/100 (Умеренный риск). Имеются сдерживающие факторы '
                '(молодой бизнес, умеренная закредитованность или исторические задержки платежей). '
                'Рекомендуется ручное андеррайтинговое рассмотрение сотрудником банка.'
            )
        else:
            risk_level = ScoringResult.RiskLevel.HIGH
            recommendation = ScoringResult.Recommendation.MANUAL_REVIEW
            explanation = (
                f'Оценка риска: {score}/100 (Повышенный риск). Существенная нагрузка на бизнес. '
                'Требуется комплексная оценка андеррайтером.'
            )

        # Remove previous scoring results for idempotency
        ScoringResult.objects.filter(application=application).delete()

        return ScoringResult.objects.create(
            application=application,
            score=score,
            risk_level=risk_level,
            recommendation=recommendation,
            factors=factors,
            stop_factors=stop_factors,
            explanation=explanation,
        )
