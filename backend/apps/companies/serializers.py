from rest_framework import serializers
from .models import Company, CompanyMembership, FinancialData


class FinancialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = [
            'id',
            'year',
            'quarter',
            'annual_revenue',
            'net_profit',
            'current_assets',
            'current_liabilities',
            'total_debt',
            'monthly_credit_payments',
            'updated_at',
        ]


class CompanySerializer(serializers.ModelSerializer):
    business_age_years = serializers.FloatField(read_only=True)
    financial_reports = FinancialDataSerializer(many=True, read_only=True)
    legal_form_display = serializers.CharField(source='get_legal_form_display', read_only=True)

    class Meta:
        model = Company
        fields = [
            'id',
            'inn',
            'ogrn',
            'kpp',
            'name',
            'short_name',
            'legal_form',
            'legal_form_display',
            'registration_date',
            'ceo_name',
            'okved',
            'okved_description',
            'legal_address',
            'tax_system',
            'is_active',
            'business_age_years',
            'financial_reports',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'business_age_years']


class CompanyMembershipSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = CompanyMembership
        fields = [
            'id',
            'company',
            'role_in_company',
            'is_signatory',
            'created_at',
        ]
