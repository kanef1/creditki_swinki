from django.db import models
from django.conf import settings
from decimal import Decimal


class CreditDecision(models.Model):
    class DecisionType(models.TextChoices):
        APPROVED = 'APPROVED', 'Одобрено'
        COUNTER_OFFER = 'COUNTER_OFFER', 'Встречное предложение'
        MANUAL_REVIEW_REQUIRED = 'MANUAL_REVIEW_REQUIRED', 'Направлено на рассмотрение андеррайтеру'
        ADDITIONAL_INFO_REQUIRED = 'ADDITIONAL_INFO_REQUIRED', 'Запрос дополнительных сведений'
        REJECTED = 'REJECTED', 'Отказано'

    class ClientResponse(models.TextChoices):
        PENDING = 'PENDING', 'Ожидает решения клиента'
        ACCEPTED = 'ACCEPTED', 'Принято клиентом'
        DECLINED = 'DECLINED', 'Отклонено клиентом'

    application = models.OneToOneField(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='decision',
        verbose_name='Кредитная заявка'
    )
    decision_type = models.CharField(
        max_length=35,
        choices=DecisionType.choices,
        verbose_name='Тип кредитного решения'
    )
    is_automated = models.BooleanField(
        default=True,
        verbose_name='Автоматическое решение системы'
    )
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Сотрудник, принявший решение'
    )
    approved_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Одобренная сумма (руб)'
    )
    approved_term_months = models.PositiveIntegerField(
        default=0,
        verbose_name='Одобренный срок (мес)'
    )
    approved_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Одобренная ставка (% годовых)'
    )
    monthly_payment = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Ежемесячный платеж (руб)'
    )
    rationale = models.TextField(
        verbose_name='Обоснование решения (для клиента)'
    )
    rejection_reasons = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Причины отказа'
    )
    underwriter_notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Внутренний комментарий андеррайтера'
    )
    client_response = models.CharField(
        max_length=20,
        choices=ClientResponse.choices,
        default=ClientResponse.PENDING,
        verbose_name='Статус ответа клиента'
    )
    client_response_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата ответа клиента'
    )
    decided_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кредитное решение'
        verbose_name_plural = 'Кредитные решения'
        ordering = ['-decided_at']

    def __str__(self):
        return f"{self.get_decision_type_display()} [Заявка #{self.application_id}]"
