from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    application = models.ForeignKey('applications.Application',on_delete=models.CASCADE)
    message = models.CharField(max_length=1000)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
