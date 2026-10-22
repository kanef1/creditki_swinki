from django.db import models
from django.conf import settings

class ScoringResult(models.Model):
    application = models.ForeignKey('applications.Application',on_delete=models.CASCADE,related_name='scores')
    revision = models.PositiveIntegerField()
    score = models.PositiveIntegerField()
    risk = models.CharField(max_length=20)
    factors = models.JSONField()
    stops = models.JSONField()
    recommendation = models.CharField(max_length=32)
    explanation = models.TextField()
    model_version = models.CharField(max_length=20,default='rules-v1')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']
        constraints = [models.UniqueConstraint(fields=['application','revision'],name='unique_scoring')]
