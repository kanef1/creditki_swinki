from django.db import models


class ScoringResult(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Низкий риск (Высокая надежность)'
        MEDIUM = 'MEDIUM', 'Умеренный риск'
        HIGH = 'HIGH', 'Повышенный риск'
        CRITICAL = 'CRITICAL', 'Критический риск'

    class Recommendation(models.TextChoices):
        AUTO_APPROVE = 'AUTO_APPROVE', 'Рекомендовано автоматическое одобрение'
        COUNTER_OFFER = 'COUNTER_OFFER', 'Рекомендовано встречное предложение (коррекция условий)'
        MANUAL_REVIEW = 'MANUAL_REVIEW', 'Требуется ручное рассмотрение андеррайтером'
        REJECT = 'REJECT', 'Рекомендован отказ'

    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='scoring_results',
        verbose_name='Кредитная заявка'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Скоринговый балл (0 - 100)'
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
        verbose_name='Уровень кредитного риска'
    )
    recommendation = models.CharField(
        max_length=30,
        choices=Recommendation.choices,
        default=Recommendation.MANUAL_REVIEW,
        verbose_name='Рекомендация скоринговой модели'
    )
    factors = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Факторы оценки риска'
    )
    stop_factors = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Выявленные стоп-факторы'
    )
    explanation = models.TextField(
        verbose_name='Текстовое обоснование скоринга'
    )
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Результат скоринговой оценки'
        verbose_name_plural = 'Результаты скоринговых оценок'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"Score {self.score}/100 [{self.get_risk_level_display()}]"
