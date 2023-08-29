from typing import Callable

from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from libs.utils.email import Email, send_email

from .models import PlanSubscription


class SingleTrialEndTask:
    def __init__(self, user_email: str) -> None:
        self.user_email = user_email

    def __call__(self) -> None:
        email = Email(
            email_to=[self.user_email],
            subject=f"[{settings.PROJECT_TITLE}] Final do período de testes do plano PRO",
            message="""Olá!\n\nSeu período de testes terminará dentro de dois (2) dias. Após este prazo, a cobrança pelo plano PRO será feita mensalmente na forma de pagamento que configurou.\n\nCaso decida cancelar o plano PRO, acesse https://diariodoclima.org.br/meus-dados e clique em "Cancelar assinatura".\n\nAtenciosamente,\nEquipe Diário do Clima.""",
        )
        send_email(email=email)


@shared_task
def single_trial_end_task(user_email: str):
    task = SingleTrialEndTask(user_email=user_email)
    task()


class DailySetupTrialEndTask:
    def __init__(self, subtask: Callable) -> None:
        self.subtask = subtask

    @property
    def query(self) -> Q:
        time_delta = timezone.timedelta(days=2)
        initial_time = timezone.datetime.today()
        final_time = initial_time + time_delta
        query_initial = Q(trial_end_at__gte=initial_time)
        query_end = Q(trial_end_at__lte=final_time)
        return query_initial & query_end

    def __call__(
        self,
    ) -> None:
        subscriptions = PlanSubscription.objects.filter(self.query).select_related(
            "user"
        )
        for subscription in subscriptions:
            self.subtask(user_email=subscription.user.email)


@shared_task
def daily_setup_trial_end_task():
    task = DailySetupTrialEndTask(subtask=single_trial_end_task.delay)
    task()
