from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class Application(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Черновик'
        SUBMITTED = 'SUBMITTED', 'Отправлена'
        VALIDATING = 'VALIDATING', 'Проверка данных'
        ENRICHING = 'ENRICHING', 'Обогащение данными (ФНС/БКИ)'
        SCORING = 'SCORING', 'Скоринг и оценка риска'
        OFFER_READY = 'OFFER_READY', 'Сформировано кредитное предложение'
        MANUAL_REVIEW = 'MANUAL_REVIEW', 'На рассмотрении андеррайтера'
        ADDITIONAL_INFO_REQUIRED = 'ADDITIONAL_INFO_REQUIRED', 'Требуются дополнительные сведения'
        ACCEPTED = 'ACCEPTED', 'Предложение принято клиентом'
        REJECTED = 'REJECTED', 'Отказано'
        COMPLETED = 'COMPLETED', 'Договор подписан / Выдано'

    application_number = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name='Номер заявки'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Заявитель'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Организация заемщика'
    )
    product = models.ForeignKey(
        'products.CreditProduct',
        on_delete=models.PROTECT,
        related_name='applications',
        verbose_name='Кредитный продукт'
    )
    requested_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Запрашиваемая сумма (руб)'
    )
    term_months = models.PositiveIntegerField(
        verbose_name='Запрашиваемый срок (мес)'
    )
    purpose = models.CharField(
        max_length=255,
        verbose_name='Цель финансирования'
    )
    additional_comments = models.TextField(
        blank=True,
        default='',
        verbose_name='Комментарии и пояснения заемщика'
    )
    status = models.CharField(
        max_length=35,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name='Текущий статус заявки'
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата и время отправки'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата завершения'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кредитная заявка'
        verbose_name_plural = 'Кредитные заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка {self.application_number} ({self.get_status_display()})"

    @classmethod
    def generate_application_number(cls) -> str:
        short_id = uuid.uuid4().hex[:6].upper()
        return f"ALFA-{short_id}"


class StatusHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Кредитная заявка'
    )
    from_status = models.CharField(
        max_length=35,
        verbose_name='Предыдущий статус'
    )
    to_status = models.CharField(
        max_length=35,
        verbose_name='Новый статус'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Кто изменил статус'
    )
    reason = models.TextField(
        blank=True,
        default='',
        verbose_name='Основание / Причина перехода'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Дополнительные параметры'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Запись истории статусов'
        verbose_name_plural = 'История статусов заявки'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.application.application_number}: {self.from_status} -> {self.to_status}"
