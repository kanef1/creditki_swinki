from rest_framework import serializers
from .models import CreditProduct


class CreditProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditProduct
        fields = [
            'id',
            'code',
            'name',
            'description',
            'target_purpose',
            'badge_text',
            'icon',
            'min_amount',
            'max_amount',
            'min_term_months',
            'max_term_months',
            'base_rate',
            'min_business_age_months',
            'requires_collateral',
            'requires_surety',
            'required_documents',
            'is_active',
            'display_order',
        ]


class LoanCalculatorInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=True)
    term_months = serializers.IntegerField(min_value=1, max_value=120, required=True)
