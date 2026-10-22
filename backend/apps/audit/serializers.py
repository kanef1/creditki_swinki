from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor',
            'actor_name',
            'action',
            'resource_type',
            'resource_id',
            'ip_address',
            'details',
            'timestamp',
        ]

    def get_actor_name(self, obj):
        if obj.actor:
            full = f"{obj.actor.first_name} {obj.actor.last_name}".strip()
            return full or obj.actor.username
        return 'СИСТЕМА (Автоматический процесс)'
