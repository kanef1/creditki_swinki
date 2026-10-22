from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Application, StatusHistory
from apps.verification.services import MockVerificationService
from apps.scoring.services import RuleBasedScoringEngine
from apps.decisions.services import CreditDecisionEngine
from apps.decisions.models import CreditDecision
from apps.notifications.models import Notification
from apps.audit.models import AuditLog


class ApplicationPipelineService:
    """
    Сквозной кредитный конвейер и конечный автомат состояний (FSM).
    Управляет переходами между статусами заявки, проверками, расчетом скоринга,
    принятием решений и аудитом.
    """

    ALLOWED_TRANSITIONS = {
        Application.Status.DRAFT: [Application.Status.SUBMITTED],
        Application.Status.SUBMITTED: [Application.Status.VALIDATING],
        Application.Status.VALIDATING: [Application.Status.ENRICHING, Application.Status.REJECTED],
        Application.Status.ENRICHING: [Application.Status.SCORING, Application.Status.REJECTED],
        Application.Status.SCORING: [
            Application.Status.OFFER_READY,
            Application.Status.MANUAL_REVIEW,
            Application.Status.REJECTED,
        ],
        Application.Status.MANUAL_REVIEW: [
            Application.Status.OFFER_READY,
            Application.Status.ADDITIONAL_INFO_REQUIRED,
            Application.Status.REJECTED,
        ],
        Application.Status.ADDITIONAL_INFO_REQUIRED: [
            Application.Status.MANUAL_REVIEW,
            Application.Status.REJECTED,
        ],
        Application.Status.OFFER_READY: [
            Application.Status.ACCEPTED,
            Application.Status.REJECTED,
        ],
        Application.Status.ACCEPTED: [Application.Status.COMPLETED],
        Application.Status.COMPLETED: [],
        Application.Status.REJECTED: [],
    }

    @classmethod
    @transaction.atomic
    def change_status(
        cls,
        application: Application,
        new_status: str,
        actor=None,
        reason: str = '',
        metadata: dict = None
    ) -> Application:
        """Валидирует и атомарно выполняет переход состояния заявки с фиксацией в истории."""
        current_status = application.status
        allowed_next = cls.ALLOWED_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next:
            raise ValidationError(
                f"Недопустимый переход статуса: из '{current_status}' в '{new_status}'."
            )

        application.status = new_status
        if new_status == Application.Status.COMPLETED:
            application.completed_at = timezone.now()
        application.save(update_fields=['status', 'completed_at', 'updated_at'])

        # Record in history
        StatusHistory.objects.create(
            application=application,
            from_status=current_status,
            to_status=new_status,
            changed_by=actor,
            reason=reason,
            metadata=metadata or {},
        )

        # Audit log
        AuditLog.objects.create(
            actor=actor,
            action=f"STATUS_TRANSITION_{new_status}",
            resource_type='Application',
            resource_id=str(application.id),
            details={
                'from_status': current_status,
                'to_status': new_status,
                'reason': reason,
            }
        )

        return application

    @classmethod
    def run_conveyor(cls, application: Application, actor=None) -> Application:
        """
        Запускает автоматический кредитный конвейер:
        DRAFT -> SUBMITTED -> VALIDATING -> ENRICHING -> SCORING -> (OFFER_READY / MANUAL_REVIEW / REJECTED)
        """
        # 1. DRAFT -> SUBMITTED
        application.submitted_at = timezone.now()
        application.save(update_fields=['submitted_at'])
        cls.change_status(
            application,
            Application.Status.SUBMITTED,
            actor=actor,
            reason='Заявка отправлена заемщиком на рассмотрение.'
        )

        # 2. SUBMITTED -> VALIDATING
        cls.change_status(
            application,
            Application.Status.VALIDATING,
            actor=actor,
            reason='Проверка полноты реквизитов и соответствия ограничениям продукта.'
        )

        # 3. VALIDATING -> ENRICHING (External checks)
        cls.change_status(
            application,
            Application.Status.ENRICHING,
            actor=actor,
            reason='Запрос и обогащение сведений из ФНС, ЕГРЮЛ и БКИ.'
        )
        MockVerificationService.run_all_checks(application)

        # 4. ENRICHING -> SCORING
        cls.change_status(
            application,
            Application.Status.SCORING,
            actor=actor,
            reason='Расчет скорингового балла и оценка факторов кредитного риска.'
        )
        scoring = RuleBasedScoringEngine.evaluate(application)

        # 5. SCORING -> Decision
        decision = CreditDecisionEngine.evaluate_automatic_decision(application)

        if decision.decision_type in (CreditDecision.DecisionType.APPROVED, CreditDecision.DecisionType.COUNTER_OFFER):
            cls.change_status(
                application,
                Application.Status.OFFER_READY,
                actor=actor,
                reason='Сформировано персональное кредитное предложение.',
                metadata={'score': scoring.score, 'decision_type': decision.decision_type}
            )
            Notification.objects.create(
                user=application.applicant,
                application=application,
                title='Вам доступно кредитное предложение!',
                message=f'По вашей заявке {application.application_number} сформировано решение. Ознакомьтесь с условиями.',
                notification_type=Notification.NotificationType.OFFER
            )
        elif decision.decision_type == CreditDecision.DecisionType.REJECTED:
            cls.change_status(
                application,
                Application.Status.REJECTED,
                actor=actor,
                reason='Отказ по результатам скоринга и проверки стоп-факторов.',
                metadata={'score': scoring.score, 'reasons': decision.rejection_reasons}
            )
            Notification.objects.create(
                user=application.applicant,
                application=application,
                title='Решение по кредитной заявке',
                message=f'К сожалению, по заявке {application.application_number} принято отрицательное решение.',
                notification_type=Notification.NotificationType.DECISION
            )
        else:
            cls.change_status(
                application,
                Application.Status.MANUAL_REVIEW,
                actor=actor,
                reason='Заявка направлена на индивидуальное рассмотрение андеррайтеру.',
                metadata={'score': scoring.score}
            )
            Notification.objects.create(
                user=application.applicant,
                application=application,
                title='Заявка передана кредитному эксперту',
                message=f'Заявка {application.application_number} находится на рассмотрении андеррайтера.',
                notification_type=Notification.NotificationType.INFO
            )

        return application

    @classmethod
    @transaction.atomic
    def underwriter_decide(
        cls,
        application: Application,
        officer_user,
        decision_type: str,
        approved_amount=None,
        approved_term_months=None,
        approved_rate=None,
        notes: str = '',
        reasons: list = None
    ) -> Application:
        """Обработка решения андеррайтером в ручном режиме."""
        if application.status not in (Application.Status.MANUAL_REVIEW, Application.Status.ADDITIONAL_INFO_REQUIRED):
            raise ValidationError('Заявка не находится на рассмотрении андеррайтера.')

        decision = CreditDecisionEngine.apply_manual_decision(
            application=application,
            officer_user=officer_user,
            decision_type=decision_type,
            approved_amount=approved_amount or application.requested_amount,
            approved_term_months=approved_term_months or application.term_months,
            approved_rate=approved_rate or application.product.base_rate,
            notes=notes,
            reasons=reasons or []
        )

        if decision_type in (CreditDecision.DecisionType.APPROVED, CreditDecision.DecisionType.COUNTER_OFFER):
            cls.change_status(
                application,
                Application.Status.OFFER_READY,
                actor=officer_user,
                reason=f"Одобрено сотрудником банка ({officer_user.get_full_name() or officer_user.username}).",
                metadata={'decision_type': decision_type, 'notes': notes}
            )
            Notification.objects.create(
                user=application.applicant,
                application=application,
                title='Кредитное предложение готово!',
                message=f'Андеррайтер рассмотрел вашу заявку {application.application_number} и подготовил предложение.',
                notification_type=Notification.NotificationType.OFFER
            )
        elif decision_type == CreditDecision.DecisionType.ADDITIONAL_INFO_REQUIRED:
            cls.change_status(
                application,
                Application.Status.ADDITIONAL_INFO_REQUIRED,
                actor=officer_user,
                reason=f"Запрос дополнительных данных: {notes}",
                metadata={'notes': notes}
            )
            Notification.objects.create(
                user=application.applicant,
                application=application,
                title='Требуется уточнение информации по заявке',
                message=f'Кредитный эксперт запросил дополнительные сведения: {notes}',
                notification_type=Notification.NotificationType.WARNING
            )
        else:
            cls.change_status(
                application,
                Application.Status.REJECTED,
                actor=officer_user,
                reason=f"Отказ андеррайтера: {notes}",
                metadata={'notes': notes, 'reasons': reasons}
            )
            Notification.objects.create(
                user=application.applicant,
                application=application,
                title='Решение по кредитной заявке',
                message=f'По вашей заявке {application.application_number} принято отрицательное решение.',
                notification_type=Notification.NotificationType.DECISION
            )

        return application

    @classmethod
    @transaction.atomic
    def client_respond_offer(cls, application: Application, client_user, accept: bool) -> Application:
        """Клиент принимает или отклоняет сформированное кредитное предложение."""
        if application.status != Application.Status.OFFER_READY:
            raise ValidationError('По данной заявке нет доступного для подписания предложения.')

        decision = application.decision
        if not decision:
            raise ValidationError('Данные кредитного решения не найдены.')

        if accept:
            decision.client_response = CreditDecision.ClientResponse.ACCEPTED
            decision.client_response_at = timezone.now()
            decision.save(update_fields=['client_response', 'client_response_at'])

            cls.change_status(
                application,
                Application.Status.ACCEPTED,
                actor=client_user,
                reason='Заемщик подтвердил согласие с предложенными условиями кредита.'
            )
            # Seamless transition to COMPLETED (contract simulated)
            cls.change_status(
                application,
                Application.Status.COMPLETED,
                actor=client_user,
                reason='Кредитный договор успешно сформирован и подписан простой ЭП. Средства зачислены.'
            )
            Notification.objects.create(
                user=client_user,
                application=application,
                title='Кредитный договор успешно оформлен!',
                message=f'Поздравляем! Финансирование по заявке {application.application_number} предоставлено.',
                notification_type=Notification.NotificationType.SUCCESS
            )
        else:
            decision.client_response = CreditDecision.ClientResponse.DECLINED
            decision.client_response_at = timezone.now()
            decision.save(update_fields=['client_response', 'client_response_at'])

            cls.change_status(
                application,
                Application.Status.REJECTED,
                actor=client_user,
                reason='Клиент отклонил предложенные банком условия.'
            )

        return application
