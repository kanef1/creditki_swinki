import os
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_create_using_real_session(settings):
    settings.PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher']
    os.environ['DEMO_PASSWORD']='Test-Password-2026!'; call_command('seed_demo')
    c=APIClient(enforce_csrf_checks=True)
    token=c.get('/api/v1/auth/csrf/').data['csrfToken']
    assert c.post('/api/v1/auth/login/',{'username':'demo_a','password':'Test-Password-2026!'},HTTP_X_CSRFTOKEN=token).status_code==200
    token=c.get('/api/v1/auth/csrf/').data['csrfToken']
    company=c.get('/api/v1/companies/').data['results'][0]
    product=c.get('/api/v1/products/').data['results'][0]
    payload={'company':company['id'],'product':product['id'],'amount':'1000000.00','term':24,'purpose':'Синтетическая закупка товаров','financial':{'revenue':'12000000.00','profit':'2400000.00','debt':'1000000.00'}}
    response=c.post('/api/v1/applications/',payload,format='json',HTTP_X_CSRFTOKEN=token)
    assert response.status_code==201
    assert c.post(f"/api/v1/applications/{response.data['id']}/submit/",HTTP_X_CSRFTOKEN=token).data['status']=='OFFER_READY'
