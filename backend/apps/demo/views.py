from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .services import DemoDataSeeder
from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer


class DemoResetDataView(APIView):
    """Сброс и восстановление эталонных демонстрационных данных хакатона."""
    permission_classes = [AllowAny]

    def post(self, request):
        result = DemoDataSeeder.seed_all()
        return Response({
            'message': 'Демонстрационные данные успешно сгенерированы.',
            'users': result['users'],
            'applications': result['applications'],
        }, status=status.HTTP_200_OK)


class DemoScenariosInfoView(APIView):
    """Справочная информация о 4 демонстрационных сценариях и учетных записях."""
    permission_classes = [AllowAny]

    def get(self, request):
        scenarios = [
            {
                'id': 'SCENARIO_A',
                'name': 'Сценарий A: Автоматическое одобрение',
                'description': 'Финансово устойчивая IT-компания (4 года на рынке, выручка 48 млн ₽, 0 долгов ФНС, отличная кредитная история).',
                'username': 'entrepreneur_a',
                'password': 'alfa2026pass',
                'role': 'ENTREPRENEUR',
                'company': 'ООО "ТехноПрогресс"',
                'inn': '7701234567',
                'expected_outcome': 'Мгновенное одобрение на запрошенных условиях (3.0 млн ₽ @ 14% годовых).',
                'application_number': 'ALFA-DEMO-001A',
            },
            {
                'id': 'SCENARIO_B',
                'name': 'Сценарий B: Встречное предложение',
                'description': 'Индивидуальный предприниматель запросил 6 млн ₽ при годовой выручке 12 млн ₽ (50% выручки - перегрузка долгового лимита).',
                'username': 'entrepreneur_b',
                'password': 'alfa2026pass',
                'role': 'ENTREPRENEUR',
                'company': 'ИП Иванов А.С.',
                'inn': '772412345678',
                'expected_outcome': 'Встречное предложение с безопасной сниженной суммой (3.5 млн ₽ @ 16.5% годовых).',
                'application_number': 'ALFA-DEMO-002B',
            },
            {
                'id': 'SCENARIO_C',
                'name': 'Сценарий C: Ручное рассмотрение андеррайтером',
                'description': 'Производственное предприятие (1.1 года на рынке, средний скоринговый балл 56/100, историческая задержка платежа в БКИ).',
                'username': 'entrepreneur_c',
                'password': 'alfa2026pass',
                'role': 'ENTREPRENEUR',
                'company': 'ООО "Вектор Плюс"',
                'inn': '7802987654',
                'expected_outcome': 'Направлено на индивидуальное рассмотрение сотруднику банка.',
                'application_number': 'ALFA-DEMO-003C',
            },
            {
                'id': 'SCENARIO_D',
                'name': 'Сценарий D: Отказ со стоп-факторами',
                'description': 'Строительная компания с задолженностью по налогам в ФНС 450 тыс. ₽, убытком и открытой просрочкой в БКИ >90 дней.',
                'username': 'entrepreneur_d',
                'password': 'alfa2026pass',
                'role': 'ENTREPRENEUR',
                'company': 'ООО "СтройНеликвид"',
                'inn': '5001999888',
                'expected_outcome': 'Отказ по стоп-факторам с прозрачным объяснением причин и рекомендациями.',
                'application_number': 'ALFA-DEMO-004D',
            },
            {
                'id': 'OFFICER',
                'name': 'Сотрудник банка (Андеррайтер)',
                'description': 'Рабочее место риск-андеррайтера: очередь кредитных заявок, оценка рисков, утверждение решений, запросы сведений.',
                'username': 'officer_alfa',
                'password': 'alfa2026pass',
                'role': 'BANK_OFFICER',
                'company': 'АО «Альфа-Банк»',
                'inn': '7728168971',
                'expected_outcome': 'Доступ к очереди заявок, детальному досье и форме принятия решений.',
                'application_number': None,
            }
        ]
        return Response({'scenarios': scenarios})


class DemoQuickLoginView(APIView):
    """Быстрый вход под выбранным демо-пользователем (удобно для жюри)."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            # Seed if not yet seeded
            DemoDataSeeder.seed_all()
            user = User.objects.filter(username=username).first()

        if not user:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': f'Авторизован как {user.first_name} {user.last_name} ({user.get_role_display()})'
        })
