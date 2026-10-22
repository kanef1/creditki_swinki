from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from decimal import Decimal
from .models import CreditProduct
from .serializers import CreditProductSerializer, LoanCalculatorInputSerializer


class CreditProductListView(generics.ListAPIView):
    """Каталог доступных кредитных продуктов для бизнеса."""
    queryset = CreditProduct.objects.filter(is_active=True)
    serializer_class = CreditProductSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CreditProductDetailView(generics.RetrieveAPIView):
    """Детальная информация по конкретному кредитному продукту."""
    queryset = CreditProduct.objects.filter(is_active=True)
    serializer_class = CreditProductSerializer
    permission_classes = [AllowAny]


class LoanCalculatorView(APIView):
    """Калькулятор ежемесячного платежа и переплаты по продукту."""
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoanCalculatorInputSerializer,
        responses={200: CreditProductSerializer}
    )
    def post(self, request):
        serializer = LoanCalculatorInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        amount = serializer.validated_data['amount']
        term = serializer.validated_data['term_months']

        product = CreditProduct.objects.filter(pk=product_id, is_active=True).first()
        if not product:
            return Response({'error': 'Кредитный продукт не найден.'}, status=status.HTTP_404_NOT_FOUND)

        monthly_payment = product.calculate_estimated_payment(amount, term)
        total_repayment = monthly_payment * term
        total_overpayment = max(Decimal('0.00'), total_repayment - amount)

        # Check product limits
        is_amount_valid = product.min_amount <= amount <= product.max_amount
        is_term_valid = product.min_term_months <= term <= product.max_term_months

        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'base_rate': product.base_rate,
            'requested_amount': amount,
            'term_months': term,
            'monthly_payment': monthly_payment,
            'total_repayment': total_repayment,
            'total_overpayment': total_overpayment,
            'is_amount_valid': is_amount_valid,
            'is_term_valid': is_term_valid,
            'min_amount': product.min_amount,
            'max_amount': product.max_amount,
            'min_term_months': product.min_term_months,
            'max_term_months': product.max_term_months,
        })
