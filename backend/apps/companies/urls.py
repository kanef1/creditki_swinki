from django.urls import path
from .views import (
    CompanyListCreateView,
    CompanyDetailView,
    CompanyLookupByInnView,
    CompanyFinancialsCreateUpdateView,
)

app_name = 'companies'

urlpatterns = [
    path('', CompanyListCreateView.as_view(), name='company_list_create'),
    path('<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('lookup/', CompanyLookupByInnView.as_view(), name='company_lookup'),
    path('<int:pk>/financials/', CompanyFinancialsCreateUpdateView.as_view(), name='company_financials'),
]
