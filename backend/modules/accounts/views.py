from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from uuid import uuid4

class LoginInput(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True,max_length=200)

class CsrfView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(responses={200:dict})
    def get(self,request): return Response({'csrfToken':get_token(request)})

@method_decorator(csrf_protect,name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'login'
    @extend_schema(request=LoginInput,responses={200:dict})
    def post(self,request):
        s = LoginInput(data=request.data); s.is_valid(raise_exception=True)
        user = authenticate(request,**s.validated_data)
        if not user: return Response({'error':{'code':400,'details':'Неверный логин или пароль'}},status=400)
        login(request,user)
        return Response({'username':user.username,'is_staff':user.is_staff})

class LogoutView(APIView):
    @extend_schema(request=None,responses={200:dict})
    def post(self,request):
        logout(request)
        return Response({'ok':True})

class ProfileView(APIView):
    @extend_schema(responses={200:dict})
    def get(self,request): return Response({'username':request.user.username,'is_staff':request.user.is_staff})

@method_decorator(csrf_protect,name='dispatch')
class VisitorView(APIView):
    """Isolated synthetic visitor context for the local embeddable demo only."""
    permission_classes = [AllowAny]
    throttle_scope = 'visitor'

    @extend_schema(request=None,responses={200:dict})
    @transaction.atomic
    def post(self,request):
        if request.user.is_authenticated and not request.user.is_staff:
            if settings.DEMO_VISITOR_ENABLED:
                from modules.companies.demo import ensure_workspace
                ensure_workspace(request.user)
            return Response({'ready':True})
        if not settings.DEMO_VISITOR_ENABLED:
            raise PermissionDenied('Демонстрационный контекст отключён. Требуется контекст основного приложения.')
        user = get_user_model().objects.create_user(username=f'visitor_{uuid4().hex}',password=None)
        from modules.companies.demo import ensure_workspace
        ensure_workspace(user)
        login(request,user,backend='django.contrib.auth.backends.ModelBackend')
        return Response({'ready':True})
