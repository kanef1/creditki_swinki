from django.contrib import admin
from .models import CreditDecision


@admin.register(CreditDecision)
class CreditDecisionAdmin(admin.ModelAdmin):
    list_display = ['application', 'decision_type', 'is_automated', 'approved_amount', 'approved_rate', 'client_response', 'decided_at']
    list_filter = ['decision_type', 'is_automated', 'client_response']
