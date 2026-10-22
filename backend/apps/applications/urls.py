from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationDetailView,
    ApplicationSubmitView,
    ApplicationProvideAdditionalInfoView,
    UnderwriterQueueView,
)

app_name = 'applications'

urlpatterns = [
    path('', ApplicationListCreateView.as_view(), name='application_list_create'),
    path('queue/', UnderwriterQueueView.as_view(), name='underwriter_queue'),
    path('<int:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
    path('<int:pk>/submit/', ApplicationSubmitView.as_view(), name='application_submit'),
    path('<int:pk>/provide-info/', ApplicationProvideAdditionalInfoView.as_view(), name='application_provide_info'),
]
