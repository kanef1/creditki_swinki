from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Company, CompanyMembership, FinancialData
from .serializers import CompanySerializer, FinancialDataSerializer
from apps.accounts.permissions import IsBankOfficer


class CompanyListCreateView(generics.ListCreateAPIView):
    """Список компаний текущего пользователя или создание новой."""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_bank_officer:
            return Company.objects.all().prefetch_related('financial_reports')
        return Company.objects.filter(memberships__user=user).prefetch_related('financial_reports')

    def perform_create(self, serializer):
        company = serializer.save()
        CompanyMembership.objects.create(
            company=company,
            user=self.request.user,
            role_in_company='Собственник / Руководитель',
            is_signatory=True
        )


class CompanyDetailView(generics.RetrieveUpdateAPIView):
    """Детальная информация о компании."""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_bank_officer:
            return Company.objects.all()
        return Company.objects.filter(memberships__user=user)


class CompanyLookupByInnView(APIView):
    """Поиск компании по ИНН (синтетический справочник ЕГРЮЛ/ФНС)."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter('inn', str, description='ИНН организации (10 или 12 цифр)', required=True)
        ],
        responses={200: CompanySerializer}
    )
    def get(self, request):
        inn = request.query_params.get('inn', '').strip()
        if not inn or not inn.isdigit() or len(inn) not in (10, 12):
            return Response(
                {'error': 'Укажите корректный ИНН (10 цифр для юрлиц или 12 цифр для ИП).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check existing in DB
        company = Company.objects.filter(inn=inn).first()
        if company:
            return Response(CompanySerializer(company).data)

        # Synthetic generator for any valid-length INN
        is_ip = len(inn) == 12
        import datetime
        mock_reg_date = (datetime.date.today() - datetime.timedelta(days=365 * 3)).isoformat()
        mock_data = {
            'inn': inn,
            'ogrn': f'1{"".join(reversed(inn))}0'[:13 if not is_ip else 15],
            'kpp': '770101001' if not is_ip else '',
            'name': f'ИП Демо Заемщик {inn[-4:]}' if is_ip else f'ООО "Альфа Бизнес {inn[-4:]}"',
            'short_name': f'ИП Демо {inn[-4:]}' if is_ip else f'ООО "АБ-{inn[-4:]}"',
            'legal_form': 'IP' if is_ip else 'LLC',
            'registration_date': mock_reg_date,
            'ceo_name': 'Иванов Алексей Сергеевич',
            'okved': '62.01',
            'okved_description': 'Разработка компьютерного программного обеспечения',
            'legal_address': f'г. Москва, ул. Цифровая, д. {int(inn[-2:]) or 1}, оф. 404',
            'tax_system': 'УСН (Доходы)',
            'is_active': True,
        }
        return Response(mock_data)


class CompanyFinancialsCreateUpdateView(APIView):
    """Добавление или обновление финансовых показателей компании."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        company = Company.objects.filter(pk=pk).first()
        if not company:
            return Response({'error': 'Компания не найдена.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        year = data.get('year')
        quarter = data.get('quarter') or None

        fin, created = FinancialData.objects.update_or_create(
            company=company,
            year=year,
            quarter=quarter,
            defaults={
                'annual_revenue': data.get('annual_revenue', 0),
                'net_profit': data.get('net_profit', 0),
                'current_assets': data.get('current_assets', 0),
                'current_liabilities': data.get('current_liabilities', 0),
                'total_debt': data.get('total_debt', 0),
                'monthly_credit_payments': data.get('monthly_credit_payments', 0),
            }
        )
        return Response(FinancialDataSerializer(fin).data, status=status.HTTP_200_OK)
