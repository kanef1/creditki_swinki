from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ENTREPRENEUR = 'ENTREPRENEUR', 'Предприниматель'
        BANK_OFFICER = 'BANK_OFFICER', 'Сотрудник банка'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ENTREPRENEUR,
        verbose_name='Роль в системе',
        help_text='Определяет доступный функционал и права'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Номер телефона'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Должность / Статус'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        role_label = self.get_role_display()
        return f"{full or self.username} ({role_label})"

    @property
    def is_entrepreneur(self) -> bool:
        return self.role == self.Role.ENTREPRENEUR

    @property
    def is_bank_officer(self) -> bool:
        return self.role == self.Role.BANK_OFFICER or self.is_staff or self.is_superuser
