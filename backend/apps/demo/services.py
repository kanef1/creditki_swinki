from decimal import Decimal
import datetime
from django.utils import timezone
from apps.accounts.models import User
from apps.companies.models import Company, CompanyMembership, FinancialData
from apps.products.models import CreditProduct
from apps.applications.models import Application
from apps.applications.services import ApplicationPipelineService


class DemoDataSeeder:
    """
    Создает демонстрационные учетные записи, кредитные продукты,
    компании и заявки для всех 4 сценариев хакатона.
    """

    @classmethod
    def seed_all(cls):
        # 1. Users
        officer = cls._create_user(
            username='officer_alfa',
            role=User.Role.BANK_OFFICER,
            first_name='Елена',
            last_name='Кузнецова',
            email='kuznetsova@alfa-bank.demo',
            position='Старший риск-андеррайтер МСП',
            phone='+7 (495) 788-88-78'
        )

        user_a = cls._create_user(
            username='entrepreneur_a',
            role=User.Role.ENTREPRENEUR,
            first_name='Алексей',
            last_name='Смирнов',
            email='smirnov@technoprogress.ru',
            position='Генеральный директор',
            phone='+7 (916) 123-45-67'
        )

        user_b = cls._create_user(
            username='entrepreneur_b',
            role=User.Role.ENTREPRENEUR,
            first_name='Иван',
            last_name='Иванов',
            email='ivanov@ip-trade.ru',
            position='Индивидуальный предприниматель',
            phone='+7 (925) 234-56-78'
        )

        user_c = cls._create_user(
            username='entrepreneur_c',
            role=User.Role.ENTREPRENEUR,
            first_name='Михаил',
            last_name='Волков',
            email='volkov@vector-plus.ru',
            position='Финансовый директор',
            phone='+7 (903) 345-67-89'
        )

        user_d = cls._create_user(
            username='entrepreneur_d',
            role=User.Role.ENTREPRENEUR,
            first_name='Денис',
            last_name='Соколов',
            email='sokolov@stroynelikvid.ru',
            position='Генеральный директор',
            phone='+7 (999) 456-78-90'
        )

        # 2. Products
        p_wc = cls._create_or_update_product(
            code='WORKING_CAPITAL',
            name='Оборотный капитал',
            description='Быстрое финансирование для пополнения оборотных средств, устранения кассовых разрывов и оптовой закупки сырья и товаров.',
            target_purpose='Пополнение оборотных средств и кассовые разрывы',
            badge_text='Быстрое решение',
            icon='TrendingUp',
            min_amount=Decimal('300000.00'),
            max_amount=Decimal('15000000.00'),
            min_term_months=3,
            max_term_months=24,
            base_rate=Decimal('14.50'),
            min_business_age_months=6,
            requires_collateral=False,
            requires_surety=False,
            display_order=1,
            required_documents=[
                'Бухгалтерский баланс (форма 1 и 2)',
                'Выписка по расчетному счету за 12 месяцев'
            ]
        )

        p_growth = cls._create_or_update_product(
            code='BUSINESS_GROWTH',
            name='Развитие и масштабирование',
            description='Кредит на открытие новых торговых точек, наем персонала, запуск маркетинговых кампаний и расширение ассортимента.',
            target_purpose='Расширение бизнеса и инвестиции в развитие',
            badge_text='Популярный выбор',
            icon='Briefcase',
            min_amount=Decimal('1000000.00'),
            max_amount=Decimal('30000000.00'),
            min_term_months=6,
            max_term_months=36,
            base_rate=Decimal('15.00'),
            min_business_age_months=12,
            requires_collateral=False,
            requires_surety=True,
            display_order=2,
            required_documents=[
                'Бухгалтерская отчетность за 2 года',
                'Паспорт поручителя',
                'План движения денежных средств (CF)'
            ]
        )

        p_equip = cls._create_or_update_product(
            code='EQUIPMENT_FINANCING',
            name='Финансирование оборудования',
            description='Целевое финансирование покупки производственного, складского и ИТ-оборудования с возможностью залога приобретаемого имущества.',
            target_purpose='Приобретение станков, техники и оборудования',
            badge_text='Выгодная ставка',
            icon='Cpu',
            min_amount=Decimal('1500000.00'),
            max_amount=Decimal('50000000.00'),
            min_term_months=12,
            max_term_months=60,
            base_rate=Decimal('13.50'),
            min_business_age_months=12,
            requires_collateral=True,
            requires_surety=False,
            display_order=3,
            required_documents=[
                'Спецификация или договор поставки оборудования',
                'Финансовая отчетность за последний отчетный год'
            ]
        )

        # 3. Companies & Financials
        # Company A (High sustainability)
        c_a = cls._create_company(
            inn='7701234567',
            ogrn='1187746123456',
            kpp='770101001',
            name='ООО "ТехноПрогресс"',
            short_name='ООО "ТехноПрогресс"',
            legal_form=Company.LegalForm.LLC,
            reg_years_ago=4,
            ceo_name='Смирнов Алексей Викторович',
            okved='62.01',
            okved_description='Разработка компьютерного программного обеспечения',
            legal_address='г. Москва, ул. Пресненский Вал, д. 14, корп. 2, оф. 501',
            tax_system='УСН (Доходы минус расходы)'
        )
        cls._create_financials(
            company=c_a,
            revenue=Decimal('48000000.00'),
            profit=Decimal('7200000.00'),
            debt=Decimal('1500000.00'),
            monthly_pmt=Decimal('85000.00')
        )
        cls._link_member(c_a, user_a)

        # Company B (Moderate leverage)
        c_b = cls._create_company(
            inn='772412345678',
            ogrn='321774600123456',
            kpp='',
            name='ИП Иванов Алексей Сергеевич',
            short_name='ИП Иванов А.С.',
            legal_form=Company.LegalForm.IP,
            reg_years_ago=2.5,
            ceo_name='Иванов Алексей Сергеевич',
            okved='47.71',
            okved_description='Розничная торговля одеждой в специализированных магазинах',
            legal_address='г. Москва, шоссе Каширское, д. 61, пав. 12',
            tax_system='УСН (Доходы)'
        )
        cls._create_financials(
            company=c_b,
            revenue=Decimal('12000000.00'),
            profit=Decimal('1800000.00'),
            debt=Decimal('2000000.00'),
            monthly_pmt=Decimal('110000.00')
        )
        cls._link_member(c_b, user_b)

        # Company C (Borderline / Manual review)
        c_c = cls._create_company(
            inn='7802987654',
            ogrn='1237847987654',
            kpp='780201001',
            name='ООО "Вектор Плюс"',
            short_name='ООО "Вектор Плюс"',
            legal_form=Company.LegalForm.LLC,
            reg_years_ago=1.1,
            ceo_name='Волков Михаил Андреевич',
            okved='25.62',
            okved_description='Обработка металлических изделий механическая',
            legal_address='г. Санкт-Петербург, Выборгская набережная, д. 45, лит. А',
            tax_system='ОСНО'
        )
        cls._create_financials(
            company=c_c,
            revenue=Decimal('25000000.00'),
            profit=Decimal('2100000.00'),
            debt=Decimal('3500000.00'),
            monthly_pmt=Decimal('180000.00')
        )
        cls._link_member(c_c, user_c)

        # Company D (Critical risk & stop factors)
        c_d = cls._create_company(
            inn='5001999888',
            ogrn='1245001999888',
            kpp='500101001',
            name='ООО "СтройНеликвид"',
            short_name='ООО "СтройНеликвид"',
            legal_form=Company.LegalForm.LLC,
            reg_years_ago=1.0,
            ceo_name='Соколов Денис Игоревич',
            okved='41.20',
            okved_description='Строительство жилых и нежилых зданий',
            legal_address='Московская область, г. Балашиха, ул. Советская, д. 3',
            tax_system='ОСНО'
        )
        cls._create_financials(
            company=c_d,
            revenue=Decimal('8000000.00'),
            profit=Decimal('-650000.00'),
            debt=Decimal('4000000.00'),
            monthly_pmt=Decimal('250000.00')
        )
        cls._link_member(c_d, user_d)

        # 4. Applications for 4 scenarios
        # Clean existing demo applications
        Application.objects.filter(application_number__startswith='ALFA-DEMO-').delete()

        # Application A (Auto-approve)
        app_a = Application.objects.create(
            application_number='ALFA-DEMO-001A',
            applicant=user_a,
            company=c_a,
            product=p_wc,
            requested_amount=Decimal('3000000.00'),
            term_months=12,
            purpose='Пополнение оборотных средств для закупки серверов и сетевого оборудования',
            status=Application.Status.DRAFT,
        )
        ApplicationPipelineService.run_conveyor(app_a, actor=user_a)

        # Application B (Counter-offer)
        app_b = Application.objects.create(
            application_number='ALFA-DEMO-002B',
            applicant=user_b,
            company=c_b,
            product=p_growth,
            requested_amount=Decimal('6000000.00'),
            term_months=36,
            purpose='Масштабирование сети: открытие двух новых магазинов одежды',
            status=Application.Status.DRAFT,
        )
        ApplicationPipelineService.run_conveyor(app_b, actor=user_b)

        # Application C (Manual review)
        app_c = Application.objects.create(
            application_number='ALFA-DEMO-003C',
            applicant=user_c,
            company=c_c,
            product=p_equip,
            requested_amount=Decimal('5000000.00'),
            term_months=24,
            purpose='Приобретение современного токарного станка с ЧПУ',
            status=Application.Status.DRAFT,
        )
        ApplicationPipelineService.run_conveyor(app_c, actor=user_c)

        # Application D (Rejection)
        app_d = Application.objects.create(
            application_number='ALFA-DEMO-004D',
            applicant=user_d,
            company=c_d,
            product=p_wc,
            requested_amount=Decimal('4000000.00'),
            term_months=12,
            purpose='Пополнение оборотных средств для закрытия кассового разрыва',
            status=Application.Status.DRAFT,
        )
        ApplicationPipelineService.run_conveyor(app_d, actor=user_d)

        return {
            'users': [officer.username, user_a.username, user_b.username, user_c.username, user_d.username],
            'applications': [
                app_a.application_number,
                app_b.application_number,
                app_c.application_number,
                app_d.application_number,
            ]
        }

    @classmethod
    def _create_user(cls, username, role, first_name, last_name, email, position, phone):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'role': role,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'position': position,
                'phone': phone,
                'is_staff': (role == User.Role.BANK_OFFICER),
            }
        )
        user.set_password('alfa2026pass')
        user.role = role
        user.save()
        return user

    @classmethod
    def _create_or_update_product(cls, code, **kwargs):
        product, _ = CreditProduct.objects.update_or_create(
            code=code,
            defaults=kwargs
        )
        return product

    @classmethod
    def _create_company(cls, inn, reg_years_ago, **kwargs):
        reg_date = datetime.date.today() - datetime.timedelta(days=int(reg_years_ago * 365.25))
        company, _ = Company.objects.update_or_create(
            inn=inn,
            defaults={
                'registration_date': reg_date,
                **kwargs
            }
        )
        return company

    @classmethod
    def _create_financials(cls, company, revenue, profit, debt, monthly_pmt):
        fin, _ = FinancialData.objects.update_or_create(
            company=company,
            year=2025,
            defaults={
                'annual_revenue': revenue,
                'net_profit': profit,
                'current_assets': revenue * Decimal('0.35'),
                'current_liabilities': debt * Decimal('0.60'),
                'total_debt': debt,
                'monthly_credit_payments': monthly_pmt,
            }
        )
        return fin

    @classmethod
    def _link_member(cls, company, user):
        CompanyMembership.objects.get_or_create(
            company=company,
            user=user,
            defaults={'role_in_company': user.position or 'Руководитель', 'is_signatory': True}
        )
