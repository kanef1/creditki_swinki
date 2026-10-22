from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Инициатор действия'
    )
    action = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Тип действия'
    )
    resource_type = models.CharField(
        max_length=50,
        verbose_name='Тип объекта'
    )
    resource_id = models.CharField(
        max_length=50,
        verbose_name='Идентификатор объекта'
    )
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        default='',
        verbose_name='IP адрес'
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Детали операции'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Время фиксации'
    )

    class Meta:
        verbose_name = 'Запись журнала аудита'
        verbose_name_plural = 'Журнал аудита'
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.actor.username if self.actor else 'SYSTEM'
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {user_str} -> {self.action} on {self.resource_type}#{self.resource_id}"
