from django.utils import timezone
from .models import Alert
from libs.services import services
from libs.querido_diario import QueridoDiarioABC
from libs.querido_diario.serializers import GazetteFilters, GazettesResult
from celery import shared_task
from accounts.models import User
from plans.models import Plan
from subscriptions.selectors import user_get_latest_plan_subscription
from libs.utils.datetime import datetime_to_date_str_diario
from typing import List
from libs.utils.email import Email, send_email


class OnlyProPlanAllowed(Exception):
    pass


class SingleAlertTask():
    def __init__(self, alert_id: str) -> None:
        self.alert_id = alert_id
        self.alert: Alert = Alert.objects.get(id=self.alert_id)

    def __call__(self, *args, **kwargs):        
        try:
            self.verify_permissions()
            self.get_gazettes()
            self.send_email_alert()
        except OnlyProPlanAllowed:
            self.send_email_call_to_pro()

    def verify_permissions(self):
        user: User = self.alert.user
        plan_subscription = user_get_latest_plan_subscription(user=user)
        self.plan: Plan = plan_subscription.plan
        if not self.plan.to_charge():
            raise OnlyProPlanAllowed()

    def get_gazettes(self) -> int:
        querido_diario: QueridoDiarioABC = services.get(QueridoDiarioABC)
        self.since: timezone.datetime = timezone.now()
        self.until: timezone.datetime = timezone.now()
        filters = GazetteFilters(
            querystring=self.alert.query_string,
            territory_id=self.alert.territory_id,
            entities=self.alert.gov_entities,
            subtheme=self.alert.sub_themes,
            since=datetime_to_date_str_diario(date=self.since),
            until=datetime_to_date_str_diario(date=self.until),
            offset=None,
            size=None,
            pre_tags=None,
            post_tags=None,
        )
        self.results: GazettesResult = querido_diario.gazettes(filters=filters)

    def email_get_alert(self) -> Email:
        message = ""
        message += str(self.results.total_gazettes)
        message += "Novos resultados de pesquisa encontrados...\n\n"
        message += "pesquisa: " + str(self.alert.query_string) + "\n"
        message += "cidade: " + str(self.alert.territory_id) + "\n"
        message += "entidades: " + str(self.alert.gov_entities) + "\n"
        message += "sub temas: " + str(self.alert.sub_themes) + "\n"
        message += datetime_to_date_str_diario(date=self.since) + "\n"
        message += datetime_to_date_str_diario(date=self.until) + "\n"

        return Email(
            subject='Diario do Clima - Alerta',
            message=message,
            email_to=[
                self.alert.user.email,
            ]
        )

    def send_email_alert(self) -> None:
        if self.results.total_gazettes > 0:
            email = self.email_get_alert()
            send_email(email=email)

    def email_get_pro_lead(self) -> Email:
        return Email(
            subject='Diario do Clima - Alerta PRO',
            message='Sua conta não é PRO mas tem alertas ativos, porque não mudar para o plano PRO?',
            email_to=[
                self.alert.user.email,
            ]
        )

    def send_email_call_to_pro(self) -> None:
        email = self.email_get_pro_lead()
        send_email(email=email)


@shared_task
def single_alert_task(alert_id: str):
    task = SingleAlertTask(alert_id=alert_id)
    task()


class DailySetupTask:
    def __init__(self, subtask) -> None:
        self.subtask = subtask

    def __call__(self) -> None:
        alerts_ids = Alert.objects.values_list('id', flat=True)
        for alert_id in alerts_ids:
            self.subtask(alert_id=alert_id)


@shared_task
def daily_setup_task():
    task = DailySetupTask(subtask=single_alert_task.delay)
    task()
