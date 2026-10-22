from django.db import models
from django.conf import settings

import uuid

class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.PROTECT)
    product = models.ForeignKey('products.CreditProduct', on_delete=models.PROTECT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creation_key = models.UUIDField(default=uuid.uuid4)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    term = models.PositiveIntegerField()
    purpose = models.CharField(max_length=1000)
    status = models.CharField(max_length=32, default='DRAFT', db_index=True)
    revision = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['created_by','creation_key'],name='unique_creation_request'),models.CheckConstraint(condition=models.Q(amount__gt=0),name='positive_amount'),models.CheckConstraint(condition=models.Q(term__gt=0),name='positive_term')]

class FinancialData(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='financial')
    revenue = models.DecimalField(max_digits=16, decimal_places=2)
    profit = models.DecimalField(max_digits=16, decimal_places=2)
    debt = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(revenue__gte=0),name='nonnegative_revenue'),models.CheckConstraint(condition=models.Q(debt__gte=0),name='nonnegative_debt')]

class StatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    previous = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=32)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']
