from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Application, StatusHistory
from modules.audit.models import AuditLog
from modules.notifications.models import Notification
from modules.scoring.models import ScoringResult
from modules.scoring.engine import evaluate
from modules.verification.services import verify
from modules.decisions.engine import recommend
from modules.decisions.models import CreditDecision

TRANSITIONS = {'DRAFT':{'SUBMITTED'},'ADDITIONAL_INFO_REQUIRED':{'SUBMITTED'},'SUBMITTED':{'VALIDATING'},'VALIDATING':{'ENRICHING'},'ENRICHING':{'SCORING'},'SCORING':{'MANUAL_REVIEW','OFFER_READY','REJECTED'},'MANUAL_REVIEW':{'OFFER_READY','REJECTED','ADDITIONAL_INFO_REQUIRED'},'OFFER_READY':{'ACCEPTED','DECLINED'},'ACCEPTED':{'COMPLETED'}}

def transition(app, status, actor, reason):
    if status not in TRANSITIONS.get(app.status,set()):
        raise ValidationError('Недопустимый переход состояния')
    old = app.status
    app.status = status
    app.save(update_fields=['status','updated_at','revision'])
    StatusHistory.objects.create(application=app,previous=old,status=status,actor=actor,reason=reason)
    AuditLog.objects.create(application=app,actor=actor,action=status,details={'previous':old,'reason':reason})
    for user_id in app.company.memberships.values_list('user_id',flat=True):
        Notification.objects.create(user_id=user_id,application=app,message=reason)

def record_decision(app, actor, status, reason, amount=None):
    CreditDecision.objects.create(application=app,revision=app.revision,outcome=status,reason=reason,amount=amount,term=app.term if amount else None,rate=app.product.rate if amount else None,actor=actor)
    transition(app,status,actor,reason)

@transaction.atomic
def submit(pk, actor):
    app = Application.objects.select_for_update().get(pk=pk)
    if app.status not in ('DRAFT','ADDITIONAL_INFO_REQUIRED'):
        return app
    if not app.purpose.strip() or app.financial.revenue <= 0:
        raise ValidationError('Укажите цель и положительную годовую выручку')
    p = app.product
    if not p.min_amount <= app.amount <= p.max_amount or not p.min_term <= app.term <= p.max_term:
        raise ValidationError('Параметры вне ограничений продукта')
    app.revision += 1
    for state in ['SUBMITTED','VALIDATING','ENRICHING']:
        transition(app,state,actor,{'SUBMITTED':'Заявка отправлена','VALIDATING':'Параметры проверены','ENRICHING':'Выполняются синтетические проверки'}[state])
    verify(app)
    transition(app,'SCORING',actor,'Рассчитывается оценка риска')
    score = ScoringResult.objects.create(application=app,revision=app.revision,**evaluate(app.company,app.financial,app.amount))
    status, reason, amount = recommend(app,score)
    if status == 'MANUAL_REVIEW': transition(app,status,actor,reason)
    else: record_decision(app,actor,status,reason,amount)
    return app

@transaction.atomic
def decide(pk, actor, data):
    app = Application.objects.select_for_update().get(pk=pk)
    status = data['outcome']
    if app.status != 'MANUAL_REVIEW':
        last = app.decisions.order_by('-id').first()
        if last and last.actor_id == actor.id and last.outcome == status and last.reason == data['reason'] and (status != 'OFFER_READY' or last.amount == data['amount']): return app
        raise ValidationError('Заявка уже обработана или не требует ручного решения')
    amount = data.get('amount') if status == 'OFFER_READY' else None
    if amount is not None and not app.product.min_amount <= amount <= min(app.amount,app.product.max_amount):
        raise ValidationError('Предложенная сумма должна быть в пределах продукта и не превышать запрошенную')
    record_decision(app,actor,status,data['reason'],amount)
    return app

@transaction.atomic
def respond(pk, actor, accept):
    app = Application.objects.select_for_update().get(pk=pk)
    target = 'COMPLETED' if accept else 'DECLINED'
    if app.status == target: return app
    if accept:
        transition(app,'ACCEPTED',actor,'Предложение принято клиентом')
        transition(app,'COMPLETED',actor,'Демонстрационный кредитный процесс завершён')
    else: transition(app,'DECLINED',actor,'Клиент отклонил предложение')
    return app
