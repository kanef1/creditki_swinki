import pytest
from decimal import Decimal
import datetime
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.companies.models import Company, FinancialData
from apps.products.models import CreditProduct
from apps.applications.models import Application


@pytest.mark.django_db
class TestApplicationsAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='api_entrepreneur',
            password='password123',
            role=User.Role.ENTREPRENEUR
        )
        self.client.force_authenticate(user=self.user)
        self.product = CreditProduct.objects.create(
            code='API_PROD',
            name='Оборотный капитал API',
            min_amount=Decimal('300000.00'),
            max_amount=Decimal('10000000.00'),
            min_term_months=3,
            max_term_months=36,
            base_rate=Decimal('14.50')
        )
        reg_date = datetime.date.today() - datetime.timedelta(days=365 * 3)
        self.company = Company.objects.create(
            inn='7701444555',
            name='ООО "API Тест Компани"',
            registration_date=reg_date,
            ceo_name='Тестовый Директор',
            okved='62.01',
            legal_address='г. Москва, ул. Арбат, 1'
        )
        FinancialData.objects.create(
            company=self.company,
            year=2025,
            annual_revenue=Decimal('30000000.00'),
            net_profit=Decimal('4500000.00'),
        )

    def test_create_draft_application(self):
        payload = {
            'company': self.company.id,
            'product': self.product.id,
            'requested_amount': '2500000.00',
            'term_months': 12,
            'purpose': 'Закупка серверного оборудования',
            'additional_comments': 'Срочная поставка',
        }
        response = self.client.post('/api/v1/applications/', payload, format='json')
        assert response.status_code == 201
        assert response.data['status'] == Application.Status.DRAFT
        assert response.data['application_number'].startswith('ALFA-')

    def test_submit_application_pipeline(self):
        # Create draft first
        app = Application.objects.create(
            application_number='ALFA-API-TEST-01',
            applicant=self.user,
            company=self.company,
            product=self.product,
            requested_amount=Decimal('2000000.00'),
            term_months=12,
            purpose='Закупка сырья',
            status=Application.Status.DRAFT
        )

        response = self.client.post(f'/api/v1/applications/{app.id}/submit/')
        assert response.status_code == 200
        assert response.data['status'] in (
            Application.Status.OFFER_READY,
            Application.Status.MANUAL_REVIEW
        )
        assert len(response.data['status_history']) > 1
        assert len(response.data['verification_results']) > 0
        assert response.data['scoring_result'] is not None

    def test_loan_calculator_api(self):
        payload = {
            'product_id': self.product.id,
            'amount': '3000000.00',
            'term_months': 12,
        }
        response = self.client.post('/api/v1/products/calculate/', payload, format='json')
        assert response.status_code == 200
        assert 'monthly_payment' in response.data
        assert 'total_repayment' in response.data
        assert Decimal(str(response.data['monthly_payment'])) > Decimal('250000.00')
