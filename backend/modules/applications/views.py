import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import Application
from .serializers import ApplicationSerializer, ManualDecisionInput
from .services import submit, decide, respond
from modules.documents.models import Document
from modules.audit.models import AuditLog

class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    http_method_names = ['get','post','patch','head','options']
    def get_queryset(self):
        qs = Application.objects.select_related('company','product','financial').prefetch_related('history__actor','verifications','scores','decisions','documents')
        if getattr(self,'swagger_fake_view',False): return qs.none()
        if not self.request.user.is_staff: qs = qs.filter(company__memberships__user=self.request.user)
        if self.action == 'list':
            if self.request.query_params.get('status'): qs = qs.filter(status=self.request.query_params['status'])
            if self.request.query_params.get('search'):
                query = self.request.query_params['search']
                qs = qs.filter(Q(company__name__icontains=query)|Q(company__inn__icontains=query))
        return qs
    def client(self):
        if self.request.user.is_staff: raise PermissionDenied('Действие доступно предпринимателю')
    def create(self,request,*args,**kwargs):
        self.client()
        key = request.data.get('creation_key')
        if key:
            try: uuid.UUID(str(key))
            except ValueError: raise ValidationError('Некорректный ключ запроса')
        # Lock the user to serialize concurrent create retries, including a missing application row.
        with transaction.atomic():
            get_user_model().objects.select_for_update().get(pk=request.user.pk)
            existing = self.get_queryset().filter(created_by=request.user,creation_key=key).first() if key else None
            if existing: return Response(self.get_serializer(existing).data)
            return super().create(request,*args,**kwargs)
    @transaction.atomic
    def partial_update(self,request,*args,**kwargs):
        self.client()
        app = self.get_object()
        app = Application.objects.select_for_update().get(pk=app.pk)
        if app.status not in ['DRAFT','ADDITIONAL_INFO_REQUIRED']: raise ValidationError('Редактирование доступно только для черновика или запроса сведений')
        serializer = self.get_serializer(app,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True); serializer.save()
        return Response(serializer.data)
    @extend_schema(request=None,responses=ApplicationSerializer)
    @action(detail=True,methods=['post'])
    def submit(self,request,pk=None):
        self.client(); app = self.get_object()
        return Response(self.get_serializer(submit(app.pk,request.user)).data)
    @extend_schema(request=ManualDecisionInput,responses=ApplicationSerializer)
    @action(detail=True,methods=['post'])
    def decision(self,request,pk=None):
        if not request.user.is_staff: raise PermissionDenied('Требуется роль сотрудника')
        app = self.get_object(); s = ManualDecisionInput(data=request.data); s.is_valid(raise_exception=True)
        return Response(self.get_serializer(decide(app.pk,request.user,s.validated_data)).data)
    @extend_schema(request=None,responses=ApplicationSerializer)
    @action(detail=True,methods=['post'])
    def accept(self,request,pk=None):
        self.client(); app = self.get_object()
        return Response(self.get_serializer(respond(app.pk,request.user,True)).data)
    @extend_schema(request=None,responses=ApplicationSerializer)
    @action(detail=True,methods=['post'])
    def decline(self,request,pk=None):
        self.client(); app = self.get_object()
        return Response(self.get_serializer(respond(app.pk,request.user,False)).data)
    @action(detail=True,methods=['post'],url_path='documents')
    def upload(self,request,pk=None):
        self.client(); app = self.get_object()
        with transaction.atomic():
            app = Application.objects.select_for_update().get(pk=app.pk)
            if app.status not in ['DRAFT','ADDITIONAL_INFO_REQUIRED']: raise ValidationError('Загрузка недоступна в этом статусе')
            file = request.FILES.get('file')
            if not file or file.size > 5*1024*1024: raise ValidationError('Выберите PDF до 5 МБ')
            if not file.name.lower().endswith('.pdf') or file.read(5) != b'%PDF-': raise ValidationError('Допустим только PDF')
            file.seek(0)
            doc = Document.objects.create(application=app,name=file.name[:200],file=file,uploaded_by=request.user)
            AuditLog.objects.create(application=app,actor=request.user,action='DOCUMENT_UPLOAD',details={'document':doc.pk})
            return Response({'id':doc.pk,'name':doc.name},status=201)
    @extend_schema(parameters=[OpenApiParameter('document_id',OpenApiTypes.INT,OpenApiParameter.PATH)],responses={(200,'application/pdf'):OpenApiTypes.BINARY})
    @action(detail=True,methods=['get'],url_path=r'documents/(?P<document_id>[^/.]+)')
    def download(self,request,pk=None,document_id=None):
        app = self.get_object()
        from django.shortcuts import get_object_or_404
        doc = get_object_or_404(app.documents,pk=document_id)
        return FileResponse(doc.file.open('rb'),as_attachment=True,filename=doc.name,content_type='application/pdf')
