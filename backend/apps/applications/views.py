from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Application, StatusHistory
from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateUpdateSerializer,
)
from .services import ApplicationPipelineService
from apps.accounts.permissions import IsBankOfficer


class ApplicationListCreateView(generics.ListCreateAPIView):
    """Список кредитных заявок или создание новой заявки (черновика)."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationCreateUpdateSerializer
        return ApplicationListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.all().select_related('company', 'product', 'applicant').prefetch_related('scoring_results')

        if not user.is_bank_officer:
            qs = qs.filter(applicant=user)

        # Filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(application_number__icontains=search) |
                Q(company__name__icontains=search) |
                Q(company__inn__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        app_number = Application.generate_application_number()
        auto_submit = serializer.validated_data.pop('auto_submit', False)

        application = serializer.save(
            applicant=user,
            application_number=app_number,
            status=Application.Status.DRAFT,
        )

        # Create initial history record
        StatusHistory.objects.create(
            application=application,
            from_status='NONE',
            to_status=Application.Status.DRAFT,
            changed_by=user,
            reason='Создана новая кредитная заявка (черновик).'
        )

        if auto_submit:
            ApplicationPipelineService.run_conveyor(application, actor=user)


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    """Детальная карточка кредитной заявки."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ApplicationCreateUpdateSerializer
        return ApplicationDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.all().select_related(
            'company', 'product', 'applicant', 'decision'
        ).prefetch_related(
            'status_history', 'verification_results', 'scoring_results', 'documents'
        )

        if not user.is_bank_officer:
            qs = qs.filter(applicant=user)
        return qs

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status != Application.Status.DRAFT and not self.request.user.is_bank_officer:
            raise ValidationError('Редактирование доступно только для заявок в статусе Черновик.')
        serializer.save()


class ApplicationSubmitView(APIView):
    """Запуск сквозного конвейера обработки кредитной заявки."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        application = generics.get_object_or_404(Application, pk=pk)

        if not user.is_bank_officer and application.applicant != user:
            raise PermissionDenied('У вас нет доступа к этой заявке.')

        if application.status != Application.Status.DRAFT:
            raise ValidationError('Отправить на проверку можно только заявку в статусе Черновик.')

        updated_app = ApplicationPipelineService.run_conveyor(application, actor=user)
        return Response(
            ApplicationDetailSerializer(updated_app).data,
            status=status.HTTP_200_OK
        )


class ApplicationProvideAdditionalInfoView(APIView):
    """Предоставление дополнительных сведений заемщиком по запросу банка."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        application = generics.get_object_or_404(Application, pk=pk, applicant=user)

        if application.status != Application.Status.ADDITIONAL_INFO_REQUIRED:
            raise ValidationError('По данной заявке не требуется предоставление дополнительных данных.')

        comment = request.data.get('comment', '').strip()
        if not comment:
            raise ValidationError({'comment': 'Укажите комментарий или пояснения.'})

        # Append comment
        if application.additional_comments:
            application.additional_comments += f"\n\n[Дополнение от заемщика]: {comment}"
        else:
            application.additional_comments = f"[Дополнение от заемщика]: {comment}"
        application.save(update_fields=['additional_comments'])

        # Transition back to MANUAL_REVIEW
        updated_app = ApplicationPipelineService.change_status(
            application,
            Application.Status.MANUAL_REVIEW,
            actor=user,
            reason=f'Заемщик предоставил запрошенные сведения: {comment[:100]}...'
        )

        return Response(
            ApplicationDetailSerializer(updated_app).data,
            status=status.HTTP_200_OK
        )


class UnderwriterQueueView(APIView):
    """Очередь заявок и сводная аналитика рабочего места андеррайтера."""
    permission_classes = [IsBankOfficer]

    @extend_schema(
        parameters=[
            OpenApiParameter('status_group', str, description='Группа статусов: review, active, all', required=False)
        ]
    )
    def get(self, request):
        status_group = request.query_params.get('status_group', 'all')
        qs = Application.objects.all().select_related('company', 'product', 'applicant').prefetch_related('scoring_results')

        if status_group == 'review':
            qs = qs.filter(status__in=[
                Application.Status.MANUAL_REVIEW,
                Application.Status.ADDITIONAL_INFO_REQUIRED
            ])
        elif status_group == 'active':
            qs = qs.filter(status__in=[
                Application.Status.SUBMITTED,
                Application.Status.VALIDATING,
                Application.Status.ENRICHING,
                Application.Status.SCORING,
                Application.Status.MANUAL_REVIEW,
                Application.Status.OFFER_READY,
            ])

        # Status summary counts
        counts = {
            'total': Application.objects.count(),
            'manual_review': Application.objects.filter(status=Application.Status.MANUAL_REVIEW).count(),
            'additional_info': Application.objects.filter(status=Application.Status.ADDITIONAL_INFO_REQUIRED).count(),
            'offer_ready': Application.objects.filter(status=Application.Status.OFFER_READY).count(),
            'completed': Application.objects.filter(status=Application.Status.COMPLETED).count(),
            'rejected': Application.objects.filter(status=Application.Status.REJECTED).count(),
            'drafts': Application.objects.filter(status=Application.Status.DRAFT).count(),
        }

        serializer = ApplicationListSerializer(qs, many=True)
        return Response({
            'counts': counts,
            'applications': serializer.data,
        })
