from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'doc_type', 'application', 'uploaded_by', 'is_verified', 'uploaded_at']
    list_filter = ['doc_type', 'is_verified']
