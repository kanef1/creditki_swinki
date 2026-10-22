from django.contrib import admin
from .models import VerificationResult


@admin.register(VerificationResult)
class VerificationResultAdmin(admin.ModelAdmin):
    list_display = ['application', 'source', 'status', 'risk_flag_raised', 'stop_factor_raised', 'created_at']
    list_filter = ['source', 'status', 'stop_factor_raised']
