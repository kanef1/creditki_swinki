from django.contrib import admin
from .models import Application, StatusHistory


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'reason', 'metadata', 'created_at']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_number',
        'company',
        'product',
        'requested_amount',
        'term_months',
        'status',
        'applicant',
        'created_at',
    ]
    list_filter = ['status', 'product']
    search_fields = ['application_number', 'company__name', 'company__inn', 'applicant__username']
    inlines = [StatusHistoryInline]
