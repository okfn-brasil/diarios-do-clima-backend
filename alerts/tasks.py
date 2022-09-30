from libs.ibge.city_abc import CityABC
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
from libs.utils.email import Email, send_email
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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

    def get_email(self):
        alert_email = self.alert.user.alert_email
        user_email = self.alert.user.email
        has_alert_email = alert_email is not None
        return alert_email if has_alert_email else user_email

    def verify_permissions(self):
        user: User = self.alert.user
        plan_subscription = user_get_latest_plan_subscription(user=user)
        self.plan: Plan = plan_subscription.plan
        if not self.plan.to_charge():
            raise OnlyProPlanAllowed()

    def get_gazettes(self) -> int:
        now = timezone.now()
        first_hour = timezone.datetime(
            now.year, now.month, now.day, hour=0, minute=0, second=0)
        last_hour = timezone.datetime(
            now.year, now.month, now.day, hour=23, minute=59, second=59)
        querido_diario: QueridoDiarioABC = services.get(QueridoDiarioABC)
        self.published_since = datetime_to_date_str_diario(date=first_hour)
        self.published_until = datetime_to_date_str_diario(date=last_hour)

        filters = GazetteFilters(
            querystring=self.alert.query_string,
            territory_id=self.alert.territory_id,
            entities=self.alert.gov_entities,
            subtheme=self.alert.sub_themes,
            published_since=self.published_since,
            published_until=self.published_until,
        )

        self.results: GazettesResult = querido_diario.gazettes(filters=filters)

    def email_get_alert(self) -> Email:
        city_api: CityABC = services.get(CityABC)
        territory_name = city_api.get_name(self.alert.territory_id)

        context = {
            'total_gazettes': self.results.total_gazettes,
            'query_string': self.alert.query_string,
            'territory_id': territory_name,
            'gov_entities': self.alert.gov_entities,
            'sub_themes': self.alert.sub_themes,
            'published_since': self.published_since,
            'published_until': self.published_until,
        }
        subject = 'Diario do Clima - Alerta'

        html_message = render_to_string('alerts/email.html', context)
        plain_message = strip_tags(html_message)

        return Email(
            subject=subject,
            message=plain_message,
            message_html=html_message,
            email_to=[
                self.get_email(),
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
                self.get_email(),
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
