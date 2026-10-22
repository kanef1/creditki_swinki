from django.db import models
from django.conf import settings
from decimal import Decimal


class Company(models.Model):
    class LegalForm(models.TextChoices):
        LLC = 'LLC', 'ООО (Общество с ограниченной ответственностью)'
        IP = 'IP', 'ИП (Индивидуальный предприниматель)'
        JSC = 'JSC', 'АО (Акционерное общество)'

    inn = models.CharField(
        max_length=12,
        unique=True,
        db_index=True,
        verbose_name='ИНН'
    )
    ogrn = models.CharField(
        max_length=15,
        blank=True,
        default='',
        verbose_name='ОГРН / ОГРНИП'
    )
    kpp = models.CharField(
        max_length=9,
        blank=True,
        default='',
        verbose_name='КПП'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Полное наименование компании'
    )
    short_name = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='Краткое наименование'
    )
    legal_form = models.CharField(
        max_length=20,
        choices=LegalForm.choices,
        default=LegalForm.LLC,
        verbose_name='Организационно-правовая форма'
    )
    registration_date = models.DateField(
        verbose_name='Дата государственной регистрации'
    )
    ceo_name = models.CharField(
        max_length=255,
        verbose_name='ФИО Руководителя'
    )
    okved = models.CharField(
        max_length=20,
        verbose_name='Основной ОКВЭД'
    )
    okved_description = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Наименование вида деятельности'
    )
    legal_address = models.TextField(
        verbose_name='Юридический адрес'
    )
    tax_system = models.CharField(
        max_length=50,
        default='УСН (Доходы минус расходы)',
        verbose_name='Система налогообложения'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Действующее предприятие'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Компания / Организация'
        verbose_name_plural = 'Компании и ИП'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.short_name or self.name} (ИНН: {self.inn})"

    @property
    def business_age_years(self) -> float:
        from django.utils import timezone
        today = timezone.now().date()
        days = (today - self.registration_date).days
        return round(days / 365.25, 1)


class CompanyMembership(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Компания'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name='Пользователь'
    )
    role_in_company = models.CharField(
        max_length=100,
        default='Генеральный директор',
        verbose_name='Роль / Должность'
    )
    is_signatory = models.BooleanField(
        default=True,
        verbose_name='Право электронной подписи'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Связь пользователя с компанией'
        verbose_name_plural = 'Связи пользователей с компаниями'
        unique_together = ('company', 'user')

    def __str__(self):
        return f"{self.user} - {self.company} ({self.role_in_company})"


class FinancialData(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='financial_reports',
        verbose_name='Компания'
    )
    year = models.PositiveIntegerField(verbose_name='Отчетный год')
    quarter = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Квартал (пусто - за год)'
    )
    annual_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Выручка (руб)'
    )
    net_profit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Чистая прибыль (руб)'
    )
    current_assets = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Оборотные активы (руб)'
    )
    current_liabilities = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Краткосрочные обязательства (руб)'
    )
    total_debt = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Общая сумма кредитных обязательств (руб)'
    )
    monthly_credit_payments = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Ежемесячный платеж по текущим кредитам (руб)'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Финансовые показатели'
        verbose_name_plural = 'Финансовые показатели'
        ordering = ['-year', '-quarter']

    def __str__(self):
        period = f"{self.year} Q{self.quarter}" if self.quarter else f"{self.year} год"
        return f"{self.company.short_name or self.company.name} [{period}]"
