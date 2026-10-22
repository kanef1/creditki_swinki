from django.contrib import admin
from .models import CreditProduct


@admin.register(CreditProduct)
class CreditProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'base_rate', 'min_amount', 'max_amount', 'min_term_months', 'max_term_months', 'is_active']
    list_filter = ['is_active', 'requires_collateral', 'requires_surety']
    search_fields = ['name', 'code']
