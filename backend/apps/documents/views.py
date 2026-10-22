from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .serializers import DocumentSerializer
from apps.accounts.permissions import IsBankOfficer
from apps.applications.models import Application


class DocumentListCreateView(generics.ListCreateAPIView):
    """Список документов или загрузка нового документа."""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        app_id = self.request.query_params.get('application_id')
        qs = Document.objects.all()
        if app_id:
            qs = qs.filter(application_id=app_id)
        if not user.is_bank_officer:
            qs = qs.filter(uploaded_by=user)
        return qs

    def perform_create(self, serializer):
        app_id = self.request.data.get('application')
        application = None
        if app_id:
            application = Application.objects.filter(pk=app_id).first()

        # If file is uploaded, extract meta
        uploaded_file = self.request.FILES.get('file')
        file_name = self.request.data.get('file_name')
        file_size = 0
        mime = 'application/pdf'

        if uploaded_file:
            file_name = file_name or uploaded_file.name
            file_size = uploaded_file.size
            mime = uploaded_file.content_type or 'application/pdf'

        serializer.save(
            uploaded_by=self.request.user,
            application=application,
            file_name=file_name or 'document.pdf',
            file_size_bytes=file_size,
            mime_type=mime,
        )


class VerifyDocumentView(APIView):
    """Проверка и акцепт документа сотрудником банка."""
    permission_classes = [IsBankOfficer]

    def post(self, request, pk):
        doc = generics.get_object_or_404(Document, pk=pk)
        is_verified = request.data.get('is_verified', True)
        notes = request.data.get('verification_notes', '')

        doc.is_verified = bool(is_verified)
        doc.verification_notes = notes
        doc.save(update_fields=['is_verified', 'verification_notes'])

        return Response(DocumentSerializer(doc).data, status=status.HTTP_200_OK)
