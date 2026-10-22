from rest_framework import serializers
from .models import ScoringResult


class ScoringResultSerializer(serializers.ModelSerializer):
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    recommendation_display = serializers.CharField(source='get_recommendation_display', read_only=True)

    class Meta:
        model = ScoringResult
        fields = [
            'id',
            'score',
            'risk_level',
            'risk_level_display',
            'recommendation',
            'recommendation_display',
            'factors',
            'stop_factors',
            'explanation',
            'calculated_at',
        ]
