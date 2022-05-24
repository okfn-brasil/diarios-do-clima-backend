from django.core.mail import send_mail
from django.utils import timezone
from celery import Task
from .models import Alert
from libs.services import services
from libs.querido_diario import QueridoDiarioABC
from libs.querido_diario.serializers import GazetteFilters, GazettesResult
from celery import shared_task
from accounts.models import User
from plans.models import Plan
from subscriptions.selectors import user_get_latest_plan_subscription
from subscriptions.models import PlanSubscription


class ProQueryNotAllowed(Exception):
    pass


class SingleAlertTask():
    def __call__(self, alert_id: str, *args, **kwargs):
        self.alert: Alert = Alert.objects.get(id=alert_id)
        try:
            self.verify_permissions()
            self.get_gazettes()
            self.send_email()
        except ProQueryNotAllowed:
            self.send_call_to_pro_email()

    def verify_permissions(self):
        user: User = self.alert.user
        plan_subscription = user_get_latest_plan_subscription(user=user)
        self.plan: Plan = plan_subscription.plan
        has_subthemes = len(self.alert.sub_themes) > 0
        if has_subthemes and not self.plan.to_charge():
            raise ProQueryNotAllowed()

    def get_gazettes(self) -> int:
        querido_diario: QueridoDiarioABC = services.get(QueridoDiarioABC)
        self.since: timezone.datetime = timezone.now()
        self.until: timezone.datetime = timezone.now()
        filters = GazetteFilters(
            querystring=self.alert.query_string,
            territory_id=self.alert.territory_id,
            entities=self.alert.gov_entites,
            subtheme=self.alert.sub_themes,
            since=None,
            until=None,
            offset=None,
            size=None,
            pre_tags=None,
            post_tags=None,
        )
        self.results: GazettesResult = querido_diario.gazettes(filters=filters)

    def send_email(self) -> None:
        if self.results.total_gazettes > 0:
            subject = 'Diario do Clima - Alerta'
            message = 'Novos resultados de pesquisa encontrados...'
            email_from = 'paulo.cruz@jurema.la'

            email_to = [
                self.alert.user.email,
            ]

            send_mail(
                subject,
                message,
                email_from,
                email_to,
                fail_silently=False,
            )

    def send_call_to_pro_email(self) -> None:
        pass


@shared_task
def single_alert_task(alert_id: str):
    task = SingleAlertTask()
    task(alert_id=alert_id)


@shared_task
def daily_setup_task():
    alerts_ids = Alert.objects.values_list('id', flat=True)
    for alert_id in alerts_ids:
        single_alert_task.delay(alert_id=alert_id)
