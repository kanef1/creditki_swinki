from rest_framework import serializers
from .models import VerificationResult


class VerificationResultSerializer(serializers.ModelSerializer):
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = VerificationResult
        fields = [
            'id',
            'source',
            'source_display',
            'status',
            'status_display',
            'risk_flag_raised',
            'stop_factor_raised',
            'summary',
            'details',
            'created_at',
        ]
