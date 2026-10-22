from django.db import models
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=200)
    inn = models.CharField(max_length=12, unique=True)
    age_months = models.PositiveIntegerField(default=36)
    active = models.BooleanField(default=True)
    tax_debt = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    overdue_days = models.PositiveIntegerField(default=0)
    credit_score = models.PositiveIntegerField(default=800)
    created_at = models.DateTimeField(auto_now_add=True)

class CompanyMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='memberships')
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','company'], name='unique_membership')]

class DemoCompany(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    company = models.OneToOneField(Company,on_delete=models.CASCADE,related_name='demo_profile')
    code = models.CharField(max_length=16)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','code'],name='unique_demo_company_per_user')]
