from django.db import models
from decimal import Decimal


class CreditProduct(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Код продукта'
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Наименование кредитного продукта'
    )
    description = models.TextField(
        verbose_name='Подробное описание'
    )
    target_purpose = models.CharField(
        max_length=255,
        default='Пополнение оборотных средств',
        verbose_name='Целевое назначение'
    )
    badge_text = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Метка / Бейдж'
    )
    icon = models.CharField(
        max_length=50,
        default='Briefcase',
        verbose_name='Иконка для UI'
    )
    min_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('300000.00'),
        verbose_name='Минимальная сумма (руб)'
    )
    max_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('15000000.00'),
        verbose_name='Максимальная сумма (руб)'
    )
    min_term_months = models.PositiveIntegerField(
        default=3,
        verbose_name='Минимальный срок (мес)'
    )
    max_term_months = models.PositiveIntegerField(
        default=36,
        verbose_name='Максимальный срок (мес)'
    )
    base_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('14.50'),
        verbose_name='Базовая ставка (% годовых)'
    )
    min_business_age_months = models.PositiveIntegerField(
        default=6,
        verbose_name='Минимальный срок работы бизнеса (мес)'
    )
    requires_collateral = models.BooleanField(
        default=False,
        verbose_name='Требуется залог'
    )
    requires_surety = models.BooleanField(
        default=False,
        verbose_name='Требуется поручительство'
    )
    required_documents = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Список требуемых документов'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен для выдачи'
    )
    display_order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Порядок отображения'
    )

    class Meta:
        verbose_name = 'Кредитный продукт'
        verbose_name_plural = 'Кредитные продукты'
        ordering = ['display_order', 'id']

    def __str__(self):
        return f"{self.name} (от {self.base_rate}%)"

    def calculate_estimated_payment(self, amount: Decimal, term_months: int) -> Decimal:
        """
        Calculates monthly annuity payment based on base_rate.
        Formula: A = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        """
        if term_months <= 0 or amount <= 0:
            return Decimal('0.00')

        monthly_rate = float(self.base_rate) / 100.0 / 12.0
        n = term_months
        if monthly_rate == 0:
            return amount / Decimal(n)

        factor = (monthly_rate * ((1 + monthly_rate) ** n)) / (((1 + monthly_rate) ** n) - 1)
        payment = float(amount) * factor
        return Decimal(str(round(payment, 2)))
