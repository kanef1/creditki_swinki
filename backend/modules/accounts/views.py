from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

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
