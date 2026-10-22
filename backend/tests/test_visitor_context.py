import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from modules.companies.models import CompanyMembership

def start_context(client):
    token=client.get('/api/v1/auth/csrf/').data['csrfToken']
    return client.post('/api/v1/context/',HTTP_X_CSRFTOKEN=token,HTTP_ORIGIN='http://127.0.0.1:8080')

@pytest.mark.django_db
def test_context_disabled_by_default(settings):
    settings.DEMO_VISITOR_ENABLED=False
    assert start_context(APIClient(enforce_csrf_checks=True)).status_code==403

@pytest.mark.django_db
def test_anonymous_context_is_private_and_repeatable(settings):
    settings.DEMO_VISITOR_ENABLED=True
    one=APIClient(enforce_csrf_checks=True); two=APIClient(enforce_csrf_checks=True)
    assert one.get('/api/v1/companies/').status_code==403
    assert start_context(one).status_code==200
    profile=one.get('/api/v1/auth/me/').data
    assert not profile['is_staff']
    user=get_user_model().objects.get(username=profile['username'])
    assert not user.has_usable_password()
    first_company=one.get('/api/v1/companies/').data['results'][0]['id']
    assert start_context(one).status_code==200
    assert CompanyMembership.objects.filter(user=user).count()==4
    assert get_user_model().objects.count()==1
    assert start_context(two).status_code==200
    second_company=two.get('/api/v1/companies/').data['results'][0]['id']
    assert first_company!=second_company
    assert one.get(f'/api/v1/companies/{second_company}/').status_code==404
    assert one.post('/api/v1/context/',HTTP_ORIGIN='https://untrusted.example').status_code==403

@pytest.mark.django_db
def test_visitor_can_complete_credit_flow_without_login(settings):
    from django.core.management import call_command
    import os
    os.environ['DEMO_PASSWORD']='Synthetic-Test-2026!';call_command('seed_demo')
    settings.DEMO_VISITOR_ENABLED=True
    client=APIClient(enforce_csrf_checks=True); other=APIClient(enforce_csrf_checks=True)
    assert start_context(client).status_code==200
    company=client.get('/api/v1/companies/').data['results'][0]
    product=client.get('/api/v1/products/').data['results'][0]
    token=client.get('/api/v1/auth/csrf/').data['csrfToken']
    headers={'HTTP_X_CSRFTOKEN':token,'HTTP_ORIGIN':'http://127.0.0.1:8080'}
    response=client.post('/api/v1/applications/',{'company':company['id'],'product':product['id'],'amount':'1000000.00','term':24,'purpose':'Синтетическая закупка оборудования','financial':{'revenue':'12000000.00','profit':'2400000.00','debt':'1000000.00'}},format='json',**headers)
    assert response.status_code==201
    path=f"/api/v1/applications/{response.data['id']}/"
    assert client.post(path+'submit/',**headers).data['status']=='OFFER_READY'
    assert client.post(path+'accept/',**headers).data['status']=='COMPLETED'
    assert start_context(other).status_code==200
    assert other.get(path).status_code==404
