from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        INFO = 'INFO', 'Информация'
        SUCCESS = 'SUCCESS', 'Успех'
        WARNING = 'WARNING', 'Внимание'
        OFFER = 'OFFER', 'Кредитное предложение'
        DECISION = 'DECISION', 'Решение банка'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь'
    )
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Заявка'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок уведомления'
    )
    message = models.TextField(
        verbose_name='Текст уведомления'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        verbose_name='Тип уведомления'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"
