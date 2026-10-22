from django.urls import path
from .views import ScoringResultDetailView

app_name = 'scoring'

urlpatterns = [
    path('application/<int:application_id>/', ScoringResultDetailView.as_view(), name='scoring_detail'),
]
