from django.utils import timezone
from .models import PlanSubscription
from celery import shared_task
from accounts.models import User
from typing import List, Callable
from libs.utils.email import Email, send_email
from django.db.models import Q


class SingleTrialEndTask:
    def __init__(self, user: User) -> None:
        self.user = user

    def __call__(self) -> None:
        email = Email(
            email_to=[self.user.email],
            subject="Diario do Clima final do periodo de teste",
            message="Seu trial terminam em dois(2) dias.",
        )
        send_email(email=email)


@shared_task
def single_trial_end_task(user: User):
    task = SingleTrialEndTask(user=user)
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

    def __call__(self,) -> None:
        subscriptions = PlanSubscription.objects.filter(
            self.query).select_related('user')
        for subscription in subscriptions:
            self.subtask(user=subscription.user)


@shared_task
def daily_setup_trial_end_task():
    task = DailySetupTrialEndTask(subtask=single_trial_end_task.delay)
    task()
