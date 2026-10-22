import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4
import pytest
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection, close_old_connections
from rest_framework.test import APIClient
from modules.applications.models import Application
from modules.applications.services import transition
from modules.scoring.engine import evaluate
from rest_framework.exceptions import ValidationError

@pytest.fixture
def seeded(db):
    os.environ['DEMO_PASSWORD'] = 'Test-Password-2026!'
    call_command('seed_demo')
    return get_user_model()

def client_for(User, name):
    c = APIClient(); c.force_authenticate(User.objects.get(username=name)); return c

@pytest.mark.parametrize('name,status,amount',[('demo_a','OFFER_READY','1000000.00'),('demo_b','OFFER_READY','1800000.00'),('demo_c','MANUAL_REVIEW',None),('demo_d','REJECTED',None)])
def test_four_scenarios(seeded,name,status,amount):
    c = client_for(seeded,name)
    app = c.get('/api/v1/applications/').data['results'][0]
    assert app['status'] == status
    assert len(app['verifications']) == 2
    assert len(app['scores']) == 1
    if amount: assert app['decisions'][-1]['amount'] == amount
    initial = len(app['history'])
    repeated = c.post(f"/api/v1/applications/{app['id']}/submit/")
    assert repeated.status_code == 200
    assert len(repeated.data['history']) == initial

def test_manual_info_resubmit_accept(seeded):
    bank=client_for(seeded,'bank'); client=client_for(seeded,'demo_c')
    a=client.get('/api/v1/applications/').data['results'][0]; path=f"/api/v1/applications/{a['id']}/"
    assert bank.post(path+'decision/',{'outcome':'ADDITIONAL_INFO_REQUIRED','reason':'Предоставьте обновлённые финансовые сведения'},format='json').status_code==200
    assert client.patch(path,{'purpose':'Обновлённые сведения о закупке оборудования'},format='json').status_code==200
    assert client.post(path+'submit/').data['status']=='MANUAL_REVIEW'
    data={'outcome':'OFFER_READY','reason':'Показатели изучены, кредит согласован','amount':'900000.00'}
    assert bank.post(path+'decision/',data,format='json').data['status']=='OFFER_READY'
    assert bank.post(path+'decision/',data,format='json').status_code==200
    assert bank.post(path+'decision/',{'outcome':'REJECTED','reason':'Противоречащее решение запрещено'},format='json').status_code==400
    assert client.post(path+'accept/').data['status']=='COMPLETED'
    n=len(client.get(path).data['history'])
    assert client.post(path+'accept/').status_code==200
    assert len(client.get(path).data['history'])==n
    assert client.post(path+'decline/').status_code==400

def test_access_and_validation(seeded):
    a=Application.objects.filter(created_by__username='demo_a').first(); path=f'/api/v1/applications/{a.pk}/'
    other=client_for(seeded,'demo_b'); owner=client_for(seeded,'demo_a'); bank=client_for(seeded,'bank')
    assert APIClient().get('/api/v1/applications/').status_code==403
    assert other.get(path).status_code==404
    assert other.post(path+'accept/').status_code==404
    assert owner.post(path+'decision/',{},format='json').status_code==403
    assert bank.post(path+'accept/').status_code==403
    assert owner.patch(path,{'amount':'200000.00'},format='json').status_code==400
    assert bank.post('/api/v1/applications/',{},format='json').status_code==403
    with pytest.raises(ValidationError): transition(a,'DRAFT',a.created_by,'invalid')
    payload={'company':a.company_id,'product':a.product_id,'amount':'1.00','term':24,'purpose':'Закупка оборудования','financial':{'revenue':'1000000.00','profit':'200000.00','debt':'0.00'}}
    assert owner.post('/api/v1/applications/',payload,format='json').status_code==400
    payload['amount']='200000.00'; payload['creation_key']=str(uuid4())
    new=owner.post('/api/v1/applications/',payload,format='json'); assert new.status_code==201
    assert owner.post('/api/v1/applications/',payload,format='json').data['id']==new.data['id']
    assert owner.patch(f"/api/v1/applications/{new.data['id']}/",{'company':a.company_id+1},format='json').status_code==400

def test_scoring_changes_with_inputs(seeded):
    a=Application.objects.filter(created_by__username='demo_a').first()
    high=evaluate(a.company,a.financial,a.amount)
    a.financial.profit=Decimal('-10');a.financial.debt=Decimal('99000000')
    low=evaluate(a.company,a.financial,a.amount)
    assert high['score']>low['score']
    a.company.active=False
    assert evaluate(a.company,a.financial,a.amount)['stops']

def test_csrf_login_logout(seeded):
    c=APIClient(enforce_csrf_checks=True)
    assert c.post('/api/v1/auth/login/',{'username':'demo_a','password':'Test-Password-2026!'}).status_code==403
    token=c.get('/api/v1/auth/csrf/').data['csrfToken']
    assert c.post('/api/v1/auth/login/',{'username':'demo_a','password':'wrong'},HTTP_X_CSRFTOKEN=token).status_code==400
    assert c.post('/api/v1/auth/login/',{'username':'demo_a','password':'Test-Password-2026!'},HTTP_X_CSRFTOKEN=token).status_code==200
    assert c.get('/api/v1/auth/me/').status_code==200
    token=c.get('/api/v1/auth/csrf/').data['csrfToken']
    assert c.post('/api/v1/auth/logout/',HTTP_X_CSRFTOKEN=token).status_code==200
    assert c.get('/api/v1/auth/me/').status_code==403

@pytest.mark.django_db(transaction=True)
def test_upload_security(seeded):
    from django.core.files.uploadedfile import SimpleUploadedFile
    client=client_for(seeded,'demo_c'); bank=client_for(seeded,'bank')
    a=Application.objects.filter(created_by__username='demo_c').first();path=f'/api/v1/applications/{a.pk}/'
    bank.post(path+'decision/',{'outcome':'ADDITIONAL_INFO_REQUIRED','reason':'Приложите синтетический финансовый отчёт'},format='json')
    assert client.post(path+'documents/',{'file':SimpleUploadedFile('bad.pdf',b'not pdf')},format='multipart').status_code==400
    doc=client.post(path+'documents/',{'file':SimpleUploadedFile('report.pdf',b'%PDF-1.4\n%%EOF')},format='multipart')
    assert doc.status_code==201
    url=path+f"documents/{doc.data['id']}/"
    response=client.get(url); assert response.status_code==200; response.close()
    assert client_for(seeded,'demo_b').get(url).status_code==404

@pytest.mark.django_db(transaction=True)
def test_postgres_concurrent_accept():
    if connection.vendor!='postgresql': pytest.skip('Requires PostgreSQL row locks')
    os.environ['DEMO_PASSWORD']='Test-Password-2026!';call_command('seed_demo')
    a=Application.objects.filter(created_by__username='demo_a').first()
    from modules.applications.services import respond
    def run():
        close_old_connections()
        try: return respond(a.pk,get_user_model().objects.get(username='demo_a'),True).status
        finally: close_old_connections()
    with ThreadPoolExecutor(max_workers=2) as pool: assert list(pool.map(lambda _:run(),range(2)))==['COMPLETED','COMPLETED']
    assert a.history.filter(status='ACCEPTED').count()==1
