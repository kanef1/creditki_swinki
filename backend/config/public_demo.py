from django.conf import settings
from django.http import JsonResponse


class PublicDemoMiddleware:
    def __init__(self,get_response): self.get_response=get_response

    def __call__(self,request):
        path=request.path.rstrip('/')
        if settings.PUBLIC_DEMO and (
            path in ['/api/v1/auth/login','/api/docs','/api/schema']
            or path.startswith('/admin')
            or path.endswith('/decision')
        ):
            return JsonResponse({'error':{'code':403,'details':'Служебная операция недоступна в публичной демонстрации'}},status=403)
        return self.get_response(request)
