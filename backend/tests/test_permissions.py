import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.companies.models import Company
from apps.products.models import CreditProduct
from apps.applications.models import Application


@pytest.mark.django_db
class TestPermissionsAndRoleIsolation:
    def setup_method(self):
        self.client = APIClient()
        self.entrepreneur1 = User.objects.create_user(
            username='user1', password='pass', role=User.Role.ENTREPRENEUR
        )
        self.entrepreneur2 = User.objects.create_user(
            username='user2', password='pass', role=User.Role.ENTREPRENEUR
        )
        self.officer = User.objects.create_user(
            username='officer1', password='pass', role=User.Role.BANK_OFFICER, is_staff=True
        )
        self.product = CreditProduct.objects.create(
            code='P1', name='P1', min_amount=Decimal('100000.00'), max_amount=Decimal('5000000.00'),
            min_term_months=3, max_term_months=24, base_rate=Decimal('15.00')
        )
        import datetime
        self.company = Company.objects.create(
            inn='7701999111', name='ООО Заемщик', registration_date=datetime.date.today(),
            ceo_name='Гендир', okved='62.01', legal_address='Москва'
        )
        self.app1 = Application.objects.create(
            application_number='APP-USER1',
            applicant=self.entrepreneur1,
            company=self.company,
            product=self.product,
            requested_amount=Decimal('500000.00'),
            term_months=12,
            purpose='Тест'
        )

    def test_entrepreneur_cannot_access_other_users_application(self):
        # Entrepreneur 2 tries to view Entrepreneur 1's application
        self.client.force_authenticate(user=self.entrepreneur2)
        response = self.client.get(f'/api/v1/applications/{self.app1.id}/')
        assert response.status_code == 404

    def test_entrepreneur_cannot_access_bank_queue(self):
        self.client.force_authenticate(user=self.entrepreneur1)
        response = self.client.get('/api/v1/applications/queue/')
        assert response.status_code == 403

    def test_bank_officer_can_access_bank_queue(self):
        self.client.force_authenticate(user=self.officer)
        response = self.client.get('/api/v1/applications/queue/')
        assert response.status_code == 200
        assert 'counts' in response.data
        assert 'applications' in response.data
