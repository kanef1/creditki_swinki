from django.urls import path
from .views import CreditDecisionDetailView, ManualDecisionView, ClientResponseView

app_name = 'decisions'

urlpatterns = [
    path('application/<int:application_id>/', CreditDecisionDetailView.as_view(), name='decision_detail'),
    path('application/<int:application_id>/manual/', ManualDecisionView.as_view(), name='manual_decision'),
    path('application/<int:application_id>/respond/', ClientResponseView.as_view(), name='client_respond'),
]
