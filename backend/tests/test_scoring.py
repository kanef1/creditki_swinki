import pytest
from decimal import Decimal
import datetime
from apps.accounts.models import User
from apps.companies.models import Company, FinancialData
from apps.products.models import CreditProduct
from apps.applications.models import Application
from apps.scoring.services import RuleBasedScoringEngine
from apps.scoring.models import ScoringResult
from apps.verification.services import MockVerificationService


@pytest.mark.django_db
class TestScoringEngine:
    def setup_method(self):
        self.user = User.objects.create_user(
            username='test_entrepreneur',
            password='password123',
            role=User.Role.ENTREPRENEUR
        )
        self.product = CreditProduct.objects.create(
            code='TEST_WC',
            name='Тестовый оборотный кредит',
            min_amount=Decimal('100000.00'),
            max_amount=Decimal('10000000.00'),
            min_term_months=3,
            max_term_months=24,
            base_rate=Decimal('15.00')
        )

    def test_auto_approve_scenario_scoring(self):
        # 4 years old, high revenue, high profit
        reg_date = datetime.date.today() - datetime.timedelta(days=365 * 4)
        company = Company.objects.create(
            inn='7701111111',
            name='ООО "Надежный Бизнес"',
            registration_date=reg_date,
            ceo_name='Тестов Тест',
            okved='62.01',
            legal_address='г. Москва'
        )
        FinancialData.objects.create(
            company=company,
            year=2025,
            annual_revenue=Decimal('50000000.00'),
            net_profit=Decimal('8000000.00'),
            total_debt=Decimal('1000000.00'),
            monthly_credit_payments=Decimal('50000.00')
        )
        app = Application.objects.create(
            application_number='TEST-APP-001',
            applicant=self.user,
            company=company,
            product=self.product,
            requested_amount=Decimal('2000000.00'),
            term_months=12,
            purpose='Закупка материалов',
            status=Application.Status.SUBMITTED
        )
        MockVerificationService.run_all_checks(app)
        scoring = RuleBasedScoringEngine.evaluate(app)

        assert scoring.score >= 75
        assert scoring.risk_level == ScoringResult.RiskLevel.LOW
        assert scoring.recommendation == ScoringResult.Recommendation.AUTO_APPROVE
        assert len(scoring.stop_factors) == 0

    def test_stop_factor_rejection_scoring(self):
        # Company with stop-factors (tax debt, negative profit)
        reg_date = datetime.date.today() - datetime.timedelta(days=365)
        company = Company.objects.create(
            inn='5001999888',  # triggers mock tax debt and overdue
            name='ООО "СтройНеликвид Демо"',
            registration_date=reg_date,
            ceo_name='Тестов Должник',
            okved='41.20',
            legal_address='г. Балашиха'
        )
        FinancialData.objects.create(
            company=company,
            year=2025,
            annual_revenue=Decimal('5000000.00'),
            net_profit=Decimal('-1500000.00'),
            total_debt=Decimal('4000000.00'),
            monthly_credit_payments=Decimal('200000.00')
        )
        app = Application.objects.create(
            application_number='TEST-APP-002',
            applicant=self.user,
            company=company,
            product=self.product,
            requested_amount=Decimal('3000000.00'),
            term_months=12,
            purpose='Покрытие долгов',
            status=Application.Status.SUBMITTED
        )
        MockVerificationService.run_all_checks(app)
        scoring = RuleBasedScoringEngine.evaluate(app)

        assert scoring.score < 40 or len(scoring.stop_factors) > 0
        assert scoring.risk_level in (ScoringResult.RiskLevel.CRITICAL, ScoringResult.RiskLevel.HIGH)
        assert scoring.recommendation == ScoringResult.Recommendation.REJECT
        assert len(scoring.stop_factors) > 0
