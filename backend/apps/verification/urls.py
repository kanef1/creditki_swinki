from django.urls import path
from .views import VerificationResultListView

app_name = 'verification'

urlpatterns = [
    path('', VerificationResultListView.as_view(), name='verification_list'),
]
