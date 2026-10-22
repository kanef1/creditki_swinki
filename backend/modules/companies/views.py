from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied,ValidationError
from drf_spectacular.utils import extend_schema
from .demo import catalog,profile_for,ensure_workspace,create_scenario
from .models import DemoCompany
from modules.applications.serializers import ApplicationSerializer

class ScenarioRunInput(serializers.Serializer):
    code=serializers.ChoiceField(choices=['approve','counter','manual','reject'])
    creation_key=serializers.UUIDField()

class ScenariosView(APIView):
    @extend_schema(responses={200:dict})
    def get(self,request):
        return Response({'enabled':settings.DEMO_VISITOR_ENABLED and not request.user.is_staff,'results':catalog(request.user) if settings.DEMO_VISITOR_ENABLED and not request.user.is_staff else []})

    @extend_schema(request=ScenarioRunInput,responses=ApplicationSerializer)
    @transaction.atomic
    def post(self,request):
        if not settings.DEMO_VISITOR_ENABLED or request.user.is_staff:
            raise PermissionDenied('Сценарии доступны только клиенту в локальном демо-режиме')
        s=ScenarioRunInput(data=request.data);s.is_valid(raise_exception=True)
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        ensure_workspace(request.user)
        entry=DemoCompany.objects.select_related('company').get(user=request.user,code=s.validated_data['code'])
        from modules.products.models import CreditProduct
        product=CreditProduct.objects.order_by('id').first()
        if product is None: raise ValidationError('Каталог продуктов пуст')
        app=create_scenario(request.user,entry,profile_for(entry.code),s.validated_data['creation_key'],product)
        return Response(ApplicationSerializer(app,context={'request':request}).data)
