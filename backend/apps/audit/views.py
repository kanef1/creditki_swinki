from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsBankOfficer


class AuditLogListView(generics.ListAPIView):
    """Просмотр журнала аудита (доступно только сотрудникам банка)."""
    serializer_class = AuditLogSerializer
    permission_classes = [IsBankOfficer]

    def get_queryset(self):
        qs = AuditLog.objects.all().select_related('actor')
        resource_id = self.request.query_params.get('resource_id')
        action = self.request.query_params.get('action')
        if resource_id:
            qs = qs.filter(resource_id=resource_id)
        if action:
            qs = qs.filter(action__icontains=action)
        return qs
