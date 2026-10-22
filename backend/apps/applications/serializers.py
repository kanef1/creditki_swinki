from rest_framework import serializers
from .models import Application, StatusHistory
from apps.companies.serializers import CompanySerializer
from apps.products.serializers import CreditProductSerializer
from apps.documents.serializers import DocumentSerializer
from apps.verification.serializers import VerificationResultSerializer
from apps.scoring.serializers import ScoringResultSerializer
from apps.decisions.serializers import CreditDecisionSerializer


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StatusHistory
        fields = [
            'id',
            'from_status',
            'to_status',
            'changed_by',
            'changed_by_name',
            'reason',
            'metadata',
            'created_at',
        ]

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            full = f"{obj.changed_by.first_name} {obj.changed_by.last_name}".strip()
            return full or obj.changed_by.username
        return 'Система (Автоматически)'


class ApplicationListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_inn = serializers.CharField(source='company.inn', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    applicant_name = serializers.SerializerMethodField()
    scoring_score = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'application_number',
            'company',
            'company_name',
            'company_inn',
            'product',
            'product_name',
            'requested_amount',
            'term_months',
            'purpose',
            'status',
            'status_display',
            'applicant',
            'applicant_name',
            'scoring_score',
            'risk_level',
            'submitted_at',
            'created_at',
            'updated_at',
        ]

    def get_applicant_name(self, obj):
        full = f"{obj.applicant.first_name} {obj.applicant.last_name}".strip()
        return full or obj.applicant.username

    def get_scoring_score(self, obj):
        scoring = obj.scoring_results.first()
        return scoring.score if scoring else None

    def get_risk_level(self, obj):
        scoring = obj.scoring_results.first()
        return scoring.risk_level if scoring else None


class ApplicationDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    product = CreditProductSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    verification_results = VerificationResultSerializer(many=True, read_only=True)
    scoring_result = serializers.SerializerMethodField()
    decision = CreditDecisionSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    applicant_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'application_number',
            'applicant',
            'applicant_name',
            'company',
            'product',
            'requested_amount',
            'term_months',
            'purpose',
            'additional_comments',
            'status',
            'status_display',
            'status_history',
            'verification_results',
            'scoring_result',
            'decision',
            'documents',
            'submitted_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]

    def get_applicant_name(self, obj):
        full = f"{obj.applicant.first_name} {obj.applicant.last_name}".strip()
        return full or obj.applicant.username

    def get_scoring_result(self, obj):
        scoring = obj.scoring_results.first()
        return ScoringResultSerializer(scoring).data if scoring else None


class ApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    auto_submit = serializers.BooleanField(required=False, default=False, write_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'application_number',
            'company',
            'product',
            'requested_amount',
            'term_months',
            'purpose',
            'additional_comments',
            'status',
            'auto_submit',
            'created_at',
        ]
        read_only_fields = ['id', 'application_number', 'status', 'created_at']

    def validate(self, attrs):
        product = attrs.get('product') or (self.instance.product if self.instance else None)
        amount = attrs.get('requested_amount') or (self.instance.requested_amount if self.instance else None)
        term = attrs.get('term_months') or (self.instance.term_months if self.instance else None)

        if product and amount:
            if amount < product.min_amount:
                raise serializers.ValidationError({
                    'requested_amount': f'Минимальная сумма для данного продукта: {product.min_amount:,.0f} руб.'
                })
            if amount > product.max_amount:
                raise serializers.ValidationError({
                    'requested_amount': f'Максимальная сумма для данного продукта: {product.max_amount:,.0f} руб.'
                })

        if product and term:
            if term < product.min_term_months:
                raise serializers.ValidationError({
                    'term_months': f'Минимальный срок: {product.min_term_months} мес.'
                })
            if term > product.max_term_months:
                raise serializers.ValidationError({
                    'term_months': f'Максимальный срок: {product.max_term_months} мес.'
                })

        return attrs
