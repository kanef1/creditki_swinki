from django.db import models
from django.conf import settings

class CreditDecision(models.Model):
    application = models.ForeignKey('applications.Application',on_delete=models.CASCADE,related_name='decisions')
    revision = models.PositiveIntegerField()
    outcome = models.CharField(max_length=32)
    reason = models.TextField()
    amount = models.DecimalField(max_digits=16,decimal_places=2,null=True)
    term = models.PositiveIntegerField(null=True)
    rate = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']
        constraints = [models.UniqueConstraint(fields=['application','revision'],name='unique_decision')]
