from django.db import models
from django.conf import settings


class Document(models.Model):
    class DocType(models.TextChoices):
        PASSPORT = 'PASSPORT', 'Паспорт руководителя / учредителя'
        FINANCIAL_STATEMENT = 'FINANCIAL_STATEMENT', 'Бухгалтерская отчетность (Форма 1 и 2)'
        TAX_DECLARATION = 'TAX_DECLARATION', 'Налоговая декларация (УСН / НДС)'
        BANK_STATEMENT = 'BANK_STATEMENT', 'Выписка по расчетному счету за 12 месяцев'
        CONTRACT = 'CONTRACT', 'Договор / Контракт / Спецификация'
        OTHER = 'OTHER', 'Иные подтверждающие документы'

    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        verbose_name='Кредитная заявка'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        verbose_name='Компания'
    )
    doc_type = models.CharField(
        max_length=40,
        choices=DocType.choices,
        default=DocType.FINANCIAL_STATEMENT,
        verbose_name='Тип документа'
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='Название файла'
    )
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Файл документа'
    )
    file_size_bytes = models.PositiveIntegerField(
        default=0,
        verbose_name='Размер файла в байтах'
    )
    mime_type = models.CharField(
        max_length=100,
        default='application/pdf',
        verbose_name='MIME тип'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Кто загрузил'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Проверен банком'
    )
    verification_notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Заметки андеррайтера по документу'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_doc_type_display()}: {self.file_name}"
