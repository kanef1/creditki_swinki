from django.db import models
from django.conf import settings

class Document(models.Model):
    application = models.ForeignKey('applications.Application',on_delete=models.CASCADE,related_name='documents')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
