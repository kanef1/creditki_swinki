from uuid import uuid4
import os
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from test_visitor_context import start_context

@pytest.fixture
def jury(settings,db):
    settings.DEMO_VISITOR_ENABLED=True
    os.environ['DEMO_PASSWORD']='Synthetic-Test-2026!';call_command('seed_demo')
    c=APIClient(enforce_csrf_checks=True)
    assert start_context(c).status_code==200
    token=c.get('/api/v1/auth/csrf/').data['csrfToken']
    return c,{'HTTP_X_CSRFTOKEN':token,'HTTP_ORIGIN':'http://127.0.0.1:8080'}

def test_four_companies_bootstrap_and_computed_statistics(jury):
    c,headers=jury
    scenarios=c.get('/api/v1/demo/scenarios/').data['results']
    assert len(scenarios)==4
    assert len({p['company'] for p in scenarios})==4
    assert len({p['inn'] for p in scenarios})==4
    stats=c.get('/api/v1/applications/statistics/').data
    assert stats=={'total':4,'manual':1,'offers':2,'rejected':1,'accepted':0,'offer_amount':'9500000.00'}
    apps=c.get('/api/v1/applications/').data['results']
    for profile in scenarios:
        app=next(a for a in apps if a['company']==profile['company'])
        assert app['status']==profile['expected_status']
        if profile['expected_amount']: assert app['decisions'][-1]['amount']==profile['expected_amount']
        assert len(app['scores'])==1 and len(app['verifications'])==2
    assert start_context(c).status_code==200
    assert c.get('/api/v1/applications/statistics/').data['total']==4

def test_scenario_retries_and_offer_lifecycle(jury):
    c,headers=jury;key=str(uuid4())
    payload={'code':'counter','creation_key':key}
    first=c.post('/api/v1/demo/scenarios/',payload,format='json',**headers)
    assert first.status_code==200 and first.data['decisions'][-1]['amount']=='4500000.00'
    assert c.post('/api/v1/demo/scenarios/',payload,format='json',**headers).data['id']==first.data['id']
    assert c.get('/api/v1/applications/statistics/').data['total']==5
    assert c.post('/api/v1/demo/scenarios/',{'code':'approve','creation_key':key},format='json',**headers).status_code==400
    assert c.post(f"/api/v1/applications/{first.data['id']}/decline/",**headers).status_code==200
    stats=c.get('/api/v1/applications/statistics/').data
    assert stats['offer_amount']=='9500000.00'
    offers=c.get('/api/v1/applications/offers/').data
    assert offers['count']==3
    assert next(o for o in offers['results'] if o['application']==first.data['id'])['application_status']=='DECLINED'

def test_stats_span_pages_and_history_respects_scope(jury):
    c,headers=jury
    for _ in range(22):
        assert c.post('/api/v1/demo/scenarios/',{'code':'approve','creation_key':str(uuid4())},format='json',**headers).status_code==200
    assert len(c.get('/api/v1/applications/').data['results'])==20
    stats=c.get('/api/v1/applications/statistics/').data
    assert stats['total']==26 and stats['offers']==24 and stats['offer_amount']=='119500000.00'
    history=c.get('/api/v1/applications/offers/').data
    assert history['count']==24 and history['next']
    other=APIClient(enforce_csrf_checks=True);assert start_context(other).status_code==200
    assert other.get('/api/v1/applications/statistics/').data['total']==4
    assert other.get('/api/v1/applications/offers/').data['count']==2
    foreign_id=history['results'][0]['company']['id']
    assert other.get(f'/api/v1/applications/offers/?company={foreign_id}').data['count']==0
    assert other.get(f'/api/v1/applications/statistics/?company={foreign_id}').data['total']==0

def test_jury_features_disabled_outside_demo(jury,settings):
    c,headers=jury;settings.DEMO_VISITOR_ENABLED=False
    assert c.get('/api/v1/demo/scenarios/').data=={'enabled':False,'results':[]}
    assert c.post('/api/v1/demo/scenarios/',{'code':'approve','creation_key':str(uuid4())},format='json',**headers).status_code==403
    assert APIClient().get('/api/v1/applications/statistics/').status_code==403
