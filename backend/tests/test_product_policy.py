from decimal import Decimal
import pytest
from modules.applications.models import Application
from modules.products.models import CreditProduct
from modules.applications.services import submit
from test_credit import seeded, client_for

def test_same_risk_different_product_terms(seeded):
    client = client_for(seeded,'demo_a')
    original = Application.objects.get(created_by__username='demo_a')
    results = []
    for product in CreditProduct.objects.order_by('id'):
        response = client.post('/api/v1/applications/',{
            'company': original.company_id, 'product': product.pk,
            'amount':'1000000.00','term':24,'purpose':'Синтетическое развитие бизнеса',
            'financial':{'revenue':'12000000.00','profit':'2400000.00','debt':'1000000.00'}
        },format='json')
        assert response.status_code == 201
        result = client.post(f"/api/v1/applications/{response.data['id']}/submit/").data
        assert result['status'] == 'OFFER_READY'
        assert Decimal(result['decisions'][-1]['rate']) == product.rate
        results.append(result)
    assert len({r['scores'][-1]['score'] for r in results}) == 1
    assert len({r['decisions'][-1]['rate'] for r in results}) == 3

def test_submit_rechecks_current_product_bounds(seeded):
    client = client_for(seeded,'demo_a')
    original = Application.objects.get(created_by__username='demo_a')
    response = client.post('/api/v1/applications/',{
        'company':original.company_id,'product':original.product_id,
        'amount':'1000000.00','term':24,'purpose':'Синтетическая закупка оборудования',
        'financial':{'revenue':'12000000.00','profit':'2400000.00','debt':'1000000.00'}
    },format='json')
    assert response.status_code == 201
    product = original.product
    product.max_amount = Decimal('500000.00')
    product.save(update_fields=['max_amount'])
    path = f"/api/v1/applications/{response.data['id']}/"
    assert client.post(path+'submit/').status_code == 400
    app = Application.objects.get(pk=response.data['id'])
    assert app.status == 'DRAFT'
    assert not app.scores.exists()
    assert not app.decisions.exists()
    assert app.history.count() == 1
