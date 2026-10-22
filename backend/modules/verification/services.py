from .models import VerificationResult

def verify(application):
    c = application.company
    for provider, data in [('FNS', {'active':c.active,'tax_debt':str(c.tax_debt),'age_months':c.age_months}),('BKI',{'credit_score':c.credit_score,'overdue_days':c.overdue_days})]:
        VerificationResult.objects.create(application=application,revision=application.revision,provider=provider,data={**data,'synthetic':True})
