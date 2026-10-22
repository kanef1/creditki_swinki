from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'application',
            'company',
            'doc_type',
            'doc_type_display',
            'file_name',
            'file',
            'file_size_bytes',
            'mime_type',
            'uploaded_by',
            'uploaded_by_name',
            'is_verified',
            'verification_notes',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            full = f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip()
            return full or obj.uploaded_by.username
        return 'Система'
