from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import VerificationResult
from .serializers import VerificationResultSerializer


class VerificationResultListView(generics.ListAPIView):
    """Список результатов проверок по заявке."""
    serializer_class = VerificationResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        app_id = self.request.query_params.get('application_id')
        user = self.request.user
        qs = VerificationResult.objects.all()
        if app_id:
            qs = qs.filter(application_id=app_id)
        if not user.is_bank_officer:
            qs = qs.filter(application__applicant=user)
        return qs
