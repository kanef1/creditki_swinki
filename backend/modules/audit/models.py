from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    application = models.ForeignKey('applications.Application',on_delete=models.CASCADE)
    action = models.CharField(max_length=80)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
