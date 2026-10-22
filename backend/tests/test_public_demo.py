import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from modules.products.models import CreditProduct


@pytest.mark.django_db
def test_public_catalog_creates_no_shared_accounts():
    call_command('seed_public_demo')
    assert CreditProduct.objects.count()==3
    assert get_user_model().objects.count()==0


@pytest.mark.django_db
def test_public_demo_denies_service_endpoints_and_preserves_guest_flow(settings):
    settings.PUBLIC_DEMO=True
    settings.DEMO_VISITOR_ENABLED=True
    call_command('seed_public_demo')
    client=APIClient(enforce_csrf_checks=True)
    for url in ['/api/v1/auth/login/','/api/docs/','/api/schema/','/api/v1/applications/00000000-0000-0000-0000-000000000000/decision/']:
        assert client.get(url).status_code==403
    from test_visitor_context import start_context
    assert start_context(client).status_code==200
    assert client.get('/api/v1/applications/statistics/').data['total']==4
    assert not get_user_model().objects.filter(is_staff=True).exists()
