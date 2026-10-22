from django.db import transaction
from rest_framework import serializers
from .models import Application, FinancialData, StatusHistory
from modules.companies.models import Company
from modules.products.models import CreditProduct
from modules.verification.models import VerificationResult
from modules.scoring.models import ScoringResult
from modules.decisions.models import CreditDecision
from modules.documents.models import Document

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id','name','inn','age_months']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditProduct
        fields = '__all__'

class FinancialSerializer(serializers.ModelSerializer):
    revenue = serializers.DecimalField(max_digits=16,decimal_places=2,min_value=0)
    debt = serializers.DecimalField(max_digits=16,decimal_places=2,min_value=0)
    class Meta:
        model = FinancialData
        fields = ['revenue','profit','debt']
    def validate(self,data):
        if data.get('profit',0) > data.get('revenue',0): raise serializers.ValidationError('Прибыль не может превышать выручку')
        return data

class HistorySerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source='actor.username',read_only=True)
    class Meta:
        model = StatusHistory
        fields = ['id','previous','status','actor','reason','created_at']

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationResult
        fields = ['id','revision','provider','data','created_at']

class ScoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringResult
        exclude = ['application']

class DecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditDecision
        exclude = ['application']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id','name','created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    financial = FinancialSerializer()
    company_info = CompanySerializer(source='company',read_only=True)
    product_info = ProductSerializer(source='product',read_only=True)
    history = HistorySerializer(many=True,read_only=True)
    verifications = VerificationSerializer(many=True,read_only=True)
    scores = ScoringSerializer(many=True,read_only=True)
    decisions = DecisionSerializer(many=True,read_only=True)
    documents = DocumentSerializer(many=True,read_only=True)
    class Meta:
        model = Application
        fields = ['id','company','product','company_info','product_info','amount','term','purpose','financial','creation_key','status','revision','created_at','updated_at','history','verifications','scores','decisions','documents']
        read_only_fields = ['status','revision']
    def validate(self,data):
        user = self.context['request'].user
        company = data.get('company',getattr(self.instance,'company',None))
        if user.is_staff or not company.memberships.filter(user=user).exists():
            raise serializers.ValidationError('Нет доступа к компании')
        if self.instance and company.pk != self.instance.company_id: raise serializers.ValidationError('Компанию заявки менять нельзя')
        if self.instance and 'creation_key' in data and data['creation_key'] != self.instance.creation_key:
            raise serializers.ValidationError('Ключ создания нельзя изменять')
        p = data.get('product',getattr(self.instance,'product',None))
        amount = data.get('amount',getattr(self.instance,'amount',None))
        term = data.get('term',getattr(self.instance,'term',None))
        if not p.min_amount <= amount <= p.max_amount: raise serializers.ValidationError({'amount':'Сумма вне ограничений продукта'})
        if not p.min_term <= term <= p.max_term: raise serializers.ValidationError({'term':'Срок вне ограничений продукта'})
        if not data.get('purpose',getattr(self.instance,'purpose','')).strip(): raise serializers.ValidationError({'purpose':'Укажите цель'})
        return data
    @transaction.atomic
    def create(self,data):
        financial = data.pop('financial')
        app = Application.objects.create(created_by=self.context['request'].user,**data)
        FinancialData.objects.create(application=app,**financial)
        StatusHistory.objects.create(application=app,status='DRAFT',actor=app.created_by,reason='Черновик сохранён')
        return app
    def update(self,instance,data):
        financial = data.pop('financial',None)
        if financial:
            for k,v in financial.items(): setattr(instance.financial,k,v)
            instance.financial.save()
        return super().update(instance,data)

class ManualDecisionInput(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=['OFFER_READY','REJECTED','ADDITIONAL_INFO_REQUIRED'])
    reason = serializers.CharField(min_length=10,max_length=1000)
    amount = serializers.DecimalField(max_digits=16,decimal_places=2,min_value=1,required=False)
    def validate(self,data):
        if data['outcome'] == 'OFFER_READY' and 'amount' not in data: raise serializers.ValidationError({'amount':'Укажите сумму предложения'})
        return data
