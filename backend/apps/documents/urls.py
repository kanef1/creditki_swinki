from django.urls import path
from .views import DocumentListCreateView, VerifyDocumentView

app_name = 'documents'

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='document_list_create'),
    path('<int:pk>/verify/', VerifyDocumentView.as_view(), name='document_verify'),
]
