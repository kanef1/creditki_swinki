from django.db import models


class VerificationResult(models.Model):
    class Source(models.TextChoices):
        FNS = 'FNS', 'ФНС России (Прозрачный бизнес)'
        EGRUL = 'EGRUL', 'ЕГРЮЛ / ЕГРИП'
        BKI = 'BKI', 'Бюро кредитных историй (БКИ)'
        SPARK = 'SPARK', 'СПАРК / Проверка контрагентов'
        ARBITRATION = 'ARBITRATION', 'Картотека арбитражных дел'

    class Status(models.TextChoices):
        PASSED = 'PASSED', 'Проверка пройдена'
        WARNING = 'WARNING', 'Обнаружены замечания'
        FAILED = 'FAILED', 'Критический стоп-фактор'

    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='verification_results',
        verbose_name='Кредитная заявка'
    )
    source = models.CharField(
        max_length=30,
        choices=Source.choices,
        verbose_name='Источник проверки'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PASSED,
        verbose_name='Статус проверки'
    )
    risk_flag_raised = models.BooleanField(
        default=False,
        verbose_name='Флаг повышенного риска'
    )
    stop_factor_raised = models.BooleanField(
        default=False,
        verbose_name='Сработал стоп-фактор'
    )
    summary = models.TextField(
        verbose_name='Краткое резюме проверки'
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Сырые данные проверки'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Результат внешней проверки'
        verbose_name_plural = 'Результаты внешних проверок'
        ordering = ['id']

    def __str__(self):
        return f"{self.get_source_display()} - {self.get_status_display()}"
