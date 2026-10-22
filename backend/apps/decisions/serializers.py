from rest_framework import serializers
from .models import CreditDecision


class CreditDecisionSerializer(serializers.ModelSerializer):
    decision_type_display = serializers.CharField(source='get_decision_type_display', read_only=True)
    client_response_display = serializers.CharField(source='get_client_response_display', read_only=True)
    decided_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CreditDecision
        fields = [
            'id',
            'decision_type',
            'decision_type_display',
            'is_automated',
            'decided_by',
            'decided_by_name',
            'approved_amount',
            'approved_term_months',
            'approved_rate',
            'monthly_payment',
            'rationale',
            'rejection_reasons',
            'underwriter_notes',
            'client_response',
            'client_response_display',
            'client_response_at',
            'decided_at',
            'updated_at',
        ]

    def get_decided_by_name(self, obj):
        if obj.decided_by:
            full = f"{obj.decided_by.first_name} {obj.decided_by.last_name}".strip()
            return full or obj.decided_by.username
        return 'Автоматический кредитный конвейер'


class ManualDecisionInputSerializer(serializers.Serializer):
    decision_type = serializers.ChoiceField(choices=[
        ('APPROVED', 'Одобрено'),
        ('COUNTER_OFFER', 'Встречное предложение'),
        ('ADDITIONAL_INFO_REQUIRED', 'Запрос дополнительных сведений'),
        ('REJECTED', 'Отказано'),
    ])
    approved_amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default=0)
    approved_term_months = serializers.IntegerField(required=False, default=0)
    approved_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    reasons = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class ClientResponseInputSerializer(serializers.Serializer):
    accept = serializers.BooleanField(required=True)
