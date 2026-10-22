import pytest
from decimal import Decimal
import datetime
from apps.accounts.models import User
from apps.companies.models import Company, FinancialData
from apps.products.models import CreditProduct
from apps.applications.models import Application
from apps.scoring.services import RuleBasedScoringEngine
from apps.decisions.services import CreditDecisionEngine
from apps.decisions.models import CreditDecision
from apps.verification.services import MockVerificationService


@pytest.mark.django_db
class TestDecisionEngine:
    def setup_method(self):
        self.user = User.objects.create_user(
            username='entrepreneur_test2',
            password='password123',
            role=User.Role.ENTREPRENEUR
        )
        self.officer = User.objects.create_user(
            username='officer_test2',
            password='password123',
            role=User.Role.BANK_OFFICER,
            is_staff=True
        )
        self.product = CreditProduct.objects.create(
            code='DECISION_PROD',
            name='Продукт для тестирования решений',
            min_amount=Decimal('500000.00'),
            max_amount=Decimal('20000000.00'),
            min_term_months=6,
            max_term_months=36,
            base_rate=Decimal('15.00')
        )

    def test_counter_offer_decision(self):
        # Good company but requests 60% of revenue
        reg_date = datetime.date.today() - datetime.timedelta(days=365 * 3)
        company = Company.objects.create(
            inn='7724999111',
            name='ИП Тестовый',
            registration_date=reg_date,
            ceo_name='Тест ИП',
            okved='47.11',
            legal_address='г. Москва'
        )
        FinancialData.objects.create(
            company=company,
            year=2025,
            annual_revenue=Decimal('10000000.00'),
            net_profit=Decimal('1500000.00'),
            total_debt=Decimal('1000000.00'),
            monthly_credit_payments=Decimal('50000.00')
        )
        app = Application.objects.create(
            application_number='TEST-COUNTER-01',
            applicant=self.user,
            company=company,
            product=self.product,
            requested_amount=Decimal('6000000.00'),  # 60% of revenue!
            term_months=24,
            purpose='Масштабирование',
            status=Application.Status.SUBMITTED
        )
        MockVerificationService.run_all_checks(app)
        RuleBasedScoringEngine.evaluate(app)
        decision = CreditDecisionEngine.evaluate_automatic_decision(app)

        assert decision.decision_type == CreditDecision.DecisionType.COUNTER_OFFER
        assert decision.approved_amount < Decimal('6000000.00')
        assert decision.approved_amount <= Decimal('3500000.00')

    def test_manual_officer_approval(self):
        reg_date = datetime.date.today() - datetime.timedelta(days=365 * 2)
        company = Company.objects.create(
            inn='7701555555',
            name='ООО "Рассмотрение"',
            registration_date=reg_date,
            ceo_name='Тест Директор',
            okved='62.01',
            legal_address='г. Москва'
        )
        app = Application.objects.create(
            application_number='TEST-MANUAL-01',
            applicant=self.user,
            company=company,
            product=self.product,
            requested_amount=Decimal('4000000.00'),
            term_months=12,
            purpose='Пополнение оборота',
            status=Application.Status.MANUAL_REVIEW
        )
        decision = CreditDecisionEngine.apply_manual_decision(
            application=app,
            officer_user=self.officer,
            decision_type=CreditDecision.DecisionType.APPROVED,
            approved_amount=Decimal('4000000.00'),
            approved_term_months=12,
            approved_rate=Decimal('14.50'),
            notes='Факторы риска проверены, предоставлены поручительства учредителя.'
        )

        assert decision.decision_type == CreditDecision.DecisionType.APPROVED
        assert decision.is_automated is False
        assert decision.decided_by == self.officer
        assert decision.approved_amount == Decimal('4000000.00')
