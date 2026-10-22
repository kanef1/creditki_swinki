from django.contrib import admin
from .models import ScoringResult


@admin.register(ScoringResult)
class ScoringResultAdmin(admin.ModelAdmin):
    list_display = ['application', 'score', 'risk_level', 'recommendation', 'calculated_at']
    list_filter = ['risk_level', 'recommendation']
