from django.db import models
from django.conf import settings

class CreditProduct(models.Model):
    name = models.CharField(max_length=160)
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=16, decimal_places=2)
    max_amount = models.DecimalField(max_digits=16, decimal_places=2)
    min_term = models.PositiveIntegerField(default=6)
    max_term = models.PositiveIntegerField(default=36)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(max_amount__gte=models.F('min_amount')),name='product_amount_range')]
