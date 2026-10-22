from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import CreditDecision
from .serializers import (
    CreditDecisionSerializer,
    ManualDecisionInputSerializer,
    ClientResponseInputSerializer,
)
from apps.accounts.permissions import IsBankOfficer
from apps.applications.models import Application


class CreditDecisionDetailView(generics.RetrieveAPIView):
    """Просмотр решения по заявке."""
    serializer_class = CreditDecisionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        app_id = self.kwargs.get('application_id')
        user = self.request.user
        qs = CreditDecision.objects.filter(application_id=app_id)
        if not user.is_bank_officer:
            qs = qs.filter(application__applicant=user)
        return generics.get_object_or_404(qs)


class ManualDecisionView(APIView):
    """Принятие ручного решения андеррайтером банка."""
    permission_classes = [IsBankOfficer]

    @extend_schema(request=ManualDecisionInputSerializer, responses={200: CreditDecisionSerializer})
    def post(self, request, application_id):
        serializer = ManualDecisionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = generics.get_object_or_404(Application, pk=application_id)

        from apps.applications.services import ApplicationPipelineService

        updated_app = ApplicationPipelineService.underwriter_decide(
            application=application,
            officer_user=request.user,
            decision_type=serializer.validated_data['decision_type'],
            approved_amount=serializer.validated_data.get('approved_amount'),
            approved_term_months=serializer.validated_data.get('approved_term_months'),
            approved_rate=serializer.validated_data.get('approved_rate'),
            notes=serializer.validated_data.get('notes', ''),
            reasons=serializer.validated_data.get('reasons', []),
        )

        decision = updated_app.decision
        return Response(CreditDecisionSerializer(decision).data, status=status.HTTP_200_OK)


class ClientResponseView(APIView):
    """Принятие или отклонение кредитного предложения клиентом."""
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ClientResponseInputSerializer, responses={200: CreditDecisionSerializer})
    def post(self, request, application_id):
        serializer = ClientResponseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = generics.get_object_or_404(
            Application,
            pk=application_id,
            applicant=request.user
        )

        from apps.applications.services import ApplicationPipelineService

        updated_app = ApplicationPipelineService.client_respond_offer(
            application=application,
            client_user=request.user,
            accept=serializer.validated_data['accept']
        )

        return Response({
            'message': 'Решение успешно сохранено.',
            'status': updated_app.status,
            'status_display': updated_app.get_status_display(),
            'decision': CreditDecisionSerializer(updated_app.decision).data
        }, status=status.HTTP_200_OK)
