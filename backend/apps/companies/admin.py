from django.contrib import admin
from .models import Company, CompanyMembership, FinancialData


class FinancialDataInline(admin.TabularInline):
    model = FinancialData
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'legal_form', 'ceo_name', 'registration_date', 'is_active']
    search_fields = ['name', 'inn', 'ceo_name', 'ogrn']
    list_filter = ['legal_form', 'is_active']
    inlines = [FinancialDataInline]


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ['company', 'user', 'role_in_company', 'is_signatory']
    list_filter = ['is_signatory']
