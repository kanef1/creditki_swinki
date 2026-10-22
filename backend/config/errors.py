from rest_framework.views import exception_handler
from django.http import JsonResponse

def csrf_failure(request, reason=''):
    return JsonResponse({'error': {'code': 403, 'details': 'Не удалось проверить сессию. Обновите страницу и повторите вход.'}}, status=403)

def handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {'error': {'code': response.status_code, 'details': response.data}}
    return response
