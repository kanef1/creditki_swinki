import pytest
from decimal import Decimal
import datetime
from rest_framework.exceptions import ValidationError
from apps.accounts.models import User
from apps.companies.models import Company, FinancialData
from apps.products.models import CreditProduct
from apps.applications.models import Application
from apps.applications.services import ApplicationPipelineService


@pytest.mark.django_db
class TestFsmAndStatusTransitions:
    def setup_method(self):
        self.user = User.objects.create_user(
            username='fsm_user',
            password='password123',
            role=User.Role.ENTREPRENEUR
        )
        self.officer = User.objects.create_user(
            username='fsm_officer',
            password='password123',
            role=User.Role.BANK_OFFICER,
            is_staff=True
        )
        self.product = CreditProduct.objects.create(
            code='FSM_PROD',
            name='FSM Продукт',
            min_amount=Decimal('100000.00'),
            max_amount=Decimal('5000000.00'),
            min_term_months=3,
            max_term_months=24,
            base_rate=Decimal('14.00')
        )
        reg_date = datetime.date.today() - datetime.timedelta(days=365 * 3)
        self.company = Company.objects.create(
            inn='7701333333',
            name='ООО "ФСМ Тест"',
            registration_date=reg_date,
            ceo_name='Тест Руководитель',
            okved='62.01',
            legal_address='г. Москва'
        )
        FinancialData.objects.create(
            company=self.company,
            year=2025,
            annual_revenue=Decimal('20000000.00'),
            net_profit=Decimal('3000000.00'),
        )

    def test_invalid_status_transition_raises_error(self):
        app = Application.objects.create(
            application_number='FSM-INV-01',
            applicant=self.user,
            company=self.company,
            product=self.product,
            requested_amount=Decimal('1000000.00'),
            term_months=12,
            purpose='Оборот',
            status=Application.Status.DRAFT
        )
        # Directly transitioning from DRAFT to COMPLETED is forbidden!
        with pytest.raises(ValidationError):
            ApplicationPipelineService.change_status(app, Application.Status.COMPLETED)

    def test_history_is_recorded_on_transition(self):
        app = Application.objects.create(
            application_number='FSM-HIST-01',
            applicant=self.user,
            company=self.company,
            product=self.product,
            requested_amount=Decimal('1000000.00'),
            term_months=12,
            purpose='Оборот',
            status=Application.Status.DRAFT
        )
        ApplicationPipelineService.change_status(
            app,
            Application.Status.SUBMITTED,
            actor=self.user,
            reason='Тестовая отправка заявки.'
        )

        history = app.status_history.first()
        assert history is not None
        assert history.from_status == Application.Status.DRAFT
        assert history.to_status == Application.Status.SUBMITTED
        assert history.changed_by == self.user
        assert history.reason == 'Тестовая отправка заявки.'

    def test_client_accepts_offer_lifecycle(self):
        app = Application.objects.create(
            application_number='FSM-ACC-01',
            applicant=self.user,
            company=self.company,
            product=self.product,
            requested_amount=Decimal('1000000.00'),
            term_months=12,
            purpose='Оборот',
            status=Application.Status.DRAFT
        )
        # Run conveyor
        ApplicationPipelineService.run_conveyor(app, actor=self.user)
        app.refresh_from_db()
        assert app.status == Application.Status.OFFER_READY

        # Client accepts offer
        ApplicationPipelineService.client_respond_offer(app, self.user, accept=True)
        app.refresh_from_db()
        assert app.status == Application.Status.COMPLETED
        assert app.completed_at is not None
