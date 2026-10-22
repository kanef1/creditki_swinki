import os
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

@pytest.fixture
def browser_client(settings, db):
    settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
    # Exercise both supported deployment configurations independently of the
    # process environment (Compose trusts 8080, while Vite also uses 5173).
    settings.CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:5173','http://localhost:5173','http://127.0.0.1:8080','http://localhost:8080']
    os.environ['DEMO_PASSWORD'] = 'Browser-Test-2026!'
    call_command('seed_demo')
    return APIClient(enforce_csrf_checks=True)

@pytest.mark.parametrize('origin', ['http://127.0.0.1:5173','http://localhost:5173','http://127.0.0.1:8080','http://localhost:8080'])
def test_login_with_browser_origin(browser_client, origin):
    token = browser_client.get('/api/v1/auth/csrf/').data['csrfToken']
    response = browser_client.post('/api/v1/auth/login/', {'username':'demo_a','password':'Browser-Test-2026!'}, HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN=origin)
    assert response.status_code == 200
    assert browser_client.get('/api/v1/auth/me/').data['username'] == 'demo_a'

def test_untrusted_origin_rejected_with_json(browser_client):
    token = browser_client.get('/api/v1/auth/csrf/').data['csrfToken']
    response = browser_client.post('/api/v1/auth/login/', {'username':'demo_a','password':'Browser-Test-2026!'}, HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN='https://untrusted.example')
    assert response.status_code == 403
    assert response['Content-Type'].startswith('application/json')
    assert 'error' in response.json()

def test_missing_token_still_rejected(browser_client):
    response = browser_client.post('/api/v1/auth/login/', {'username':'demo_a','password':'Browser-Test-2026!'}, HTTP_ORIGIN='http://127.0.0.1:5173')
    assert response.status_code == 403
    assert response.json()['error']['code'] == 403
