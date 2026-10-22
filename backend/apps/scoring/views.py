from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ScoringResult
from .serializers import ScoringResultSerializer


class ScoringResultDetailView(generics.RetrieveAPIView):
    """Детальный отчет о скоринге и факторах риска заявки."""
    serializer_class = ScoringResultSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        app_id = self.kwargs.get('application_id')
        user = self.request.user
        qs = ScoringResult.objects.filter(application_id=app_id)
        if not user.is_bank_officer:
            qs = qs.filter(application__applicant=user)
        return generics.get_object_or_404(qs)
