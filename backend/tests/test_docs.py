from rest_framework.test import APIClient

def test_swagger_page_renders():
    response = APIClient().get('/api/docs/')
    assert response.status_code == 200
    assert b'SwaggerUIBundle' in response.content
