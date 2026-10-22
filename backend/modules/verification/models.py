from django.db import models
from django.conf import settings

class VerificationResult(models.Model):
    application = models.ForeignKey('applications.Application',on_delete=models.CASCADE,related_name='verifications')
    revision = models.PositiveIntegerField()
    provider = models.CharField(max_length=20)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']
        constraints = [models.UniqueConstraint(fields=['application','revision','provider'],name='unique_verification')]
