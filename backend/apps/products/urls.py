from django.urls import path
from .views import CreditProductListView, CreditProductDetailView, LoanCalculatorView

app_name = 'products'

urlpatterns = [
    path('', CreditProductListView.as_view(), name='product_list'),
    path('<int:pk>/', CreditProductDetailView.as_view(), name='product_detail'),
    path('calculate/', LoanCalculatorView.as_view(), name='loan_calculate'),
]
