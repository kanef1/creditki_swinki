from decimal import Decimal
from .models import VerificationResult


class MockVerificationService:
    """
    Эмулятор интеграций с государственными реестрами и банковскими источниками данных:
    1. ФНС (ЕГРЮЛ/ЕГРИП, проверка налоговой задолженности, сервис 'Прозрачный бизнес')
    2. Бюро кредитных историй (БКИ: кредитная нагрузка, платежная дисциплина, рейтинг)
    3. Картотека арбитражных дел и СПАРК
    """

    @classmethod
    def run_all_checks(cls, application) -> list[VerificationResult]:
        """Запускает полный комплекс внешних проверок для заявки."""
        company = application.company
        # Remove any previous verification results for idempotency
        VerificationResult.objects.filter(application=application).delete()

        results = []
        results.append(cls._check_fns(application, company))
        results.append(cls._check_egrul(application, company))
        results.append(cls._check_bki(application, company))
        results.append(cls._check_arbitration(application, company))

        return results

    @classmethod
    def _check_fns(cls, application, company) -> VerificationResult:
        """Проверка налоговой службы (ФНС) на задолженности и блокировки."""
        inn = company.inn or ''
        name = company.name.lower()

        # Stop-factor check for Scenario D or company with high tax debts
        has_tax_debt = 'неликвид' in name or inn.endswith('999888') or inn.endswith('888')
        debt_amount = Decimal('450000.00') if has_tax_debt else Decimal('0.00')

        if has_tax_debt:
            status = VerificationResult.Status.FAILED
            stop_factor = True
            risk_flag = True
            summary = (
                f'ФНС: Выявлена действующая налоговая задолженность в размере {debt_amount:,.2f} руб. '
                'Приостановление операций по счетам (ст. 76 НК РФ).'
            )
        else:
            status = VerificationResult.Status.PASSED
            stop_factor = False
            risk_flag = False
            summary = 'ФНС: Задолженность по налогам и сборам отсутствует. Блокировок счетов нет.'

        details = {
            'tax_debt_rub': float(debt_amount),
            'account_blocks_count': 1 if has_tax_debt else 0,
            'tax_regime': company.tax_system,
            'reporting_discipline': 'Нарушена' if has_tax_debt else 'Своевременно',
            'check_date': '2026-10-22',
        }

        return VerificationResult.objects.create(
            application=application,
            source=VerificationResult.Source.FNS,
            status=status,
            risk_flag_raised=risk_flag,
            stop_factor_raised=stop_factor,
            summary=summary,
            details=details,
        )

    @classmethod
    def _check_egrul(cls, application, company) -> VerificationResult:
        """Проверка статуса в ЕГРЮЛ/ЕГРИП, номинальности адреса и директора."""
        inn = company.inn or ''
        name = company.name.lower()

        is_liquidating = 'ликвид' in name and not ('неликвид' in name)
        mass_director = False
        mass_address = False

        if not company.is_active or is_liquidating:
            status = VerificationResult.Status.FAILED
            stop_factor = True
            risk_flag = True
            summary = 'ЕГРЮЛ: Статус компании — в процессе ликвидации / исключения из реестра.'
        else:
            status = VerificationResult.Status.PASSED
            stop_factor = False
            risk_flag = False
            summary = f'ЕГРЮЛ: Статус действующий. Дата регистрации: {company.registration_date}. Руководитель: {company.ceo_name}.'

        details = {
            'status_text': 'Действующее' if not is_liquidating else 'Ликвидация',
            'mass_director': mass_director,
            'mass_address': mass_address,
            'ceo_inn_match': True,
            'okved_main': company.okved,
        }

        return VerificationResult.objects.create(
            application=application,
            source=VerificationResult.Source.EGRUL,
            status=status,
            risk_flag_raised=risk_flag,
            stop_factor_raised=stop_factor,
            summary=summary,
            details=details,
        )

    @classmethod
    def _check_bki(cls, application, company) -> VerificationResult:
        """Проверка кредитной истории бизнеса и учредителя (БКИ)."""
        inn = company.inn or ''
        name = company.name.lower()

        # Scenario D: high overdue
        if 'неликвид' in name or inn.endswith('999888') or inn.endswith('888'):
            bki_score = 410
            active_loans = 3
            current_overdue = 620000.0
            max_past_overdue_days = 95
            status = VerificationResult.Status.FAILED
            stop_factor = True
            risk_flag = True
            summary = 'БКИ: Критический риск. Обнаружена открытая просроченная задолженность свыше 90 дней (620 000 руб).'
        # Scenario C: past minor delay (closed)
        elif 'вектор' in name or inn.endswith('7654') or inn.endswith('654'):
            bki_score = 640
            active_loans = 1
            current_overdue = 0.0
            max_past_overdue_days = 15
            status = VerificationResult.Status.WARNING
            stop_factor = False
            risk_flag = True
            summary = 'БКИ: Умеренный риск. Текущих просрочек нет. Имелся факт задержки платежа до 15 дней 18 месяцев назад (погашен).'
        # Scenario A & B: clean credit history
        else:
            bki_score = 790
            active_loans = 1
            current_overdue = 0.0
            max_past_overdue_days = 0
            status = VerificationResult.Status.PASSED
            stop_factor = False
            risk_flag = False
            summary = 'БКИ: Высокий кредитный рейтинг заемщика. Платежная дисциплина безупречная, просрочек не зафиксировано.'

        details = {
            'bki_score': bki_score,
            'active_loans_count': active_loans,
            'current_overdue_rub': current_overdue,
            'max_past_overdue_days': max_past_overdue_days,
            'credit_history_length_months': 36,
        }

        return VerificationResult.objects.create(
            application=application,
            source=VerificationResult.Source.BKI,
            status=status,
            risk_flag_raised=risk_flag,
            stop_factor_raised=stop_factor,
            summary=summary,
            details=details,
        )

    @classmethod
    def _check_arbitration(cls, application, company) -> VerificationResult:
        """Проверка картотеки арбитражных дел и исполнительных производств (ФССП)."""
        inn = company.inn or ''
        name = company.name.lower()

        if 'неликвид' in name or inn.endswith('999888'):
            status = VerificationResult.Status.WARNING
            risk_flag = True
            stop_factor = False
            summary = 'Арбитраж: Найдено 2 открытых судебных иска в качестве ответчика на сумму 890 000 руб.'
            details = {'defendant_cases_count': 2, 'claims_sum_rub': 890000.0}
        else:
            status = VerificationResult.Status.PASSED
            risk_flag = False
            stop_factor = False
            summary = 'Арбитраж / ФССП: Судебных споров с участием заемщика не обнаружено. Исполнительных производств нет.'
            details = {'defendant_cases_count': 0, 'claims_sum_rub': 0.0}

        return VerificationResult.objects.create(
            application=application,
            source=VerificationResult.Source.ARBITRATION,
            status=status,
            risk_flag_raised=risk_flag,
            stop_factor_raised=stop_factor,
            summary=summary,
            details=details,
        )
