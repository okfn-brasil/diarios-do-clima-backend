from rest_framework.test import APITestCase
from accounts.models import User
from plans.models import Plan
from subscriptions.models import PlanSubscription
from django.core import mail
from ..tasks import SingleTrialEndTask, DailySetupTrialEndTask
from django.utils import timezone
from ..selectors import user_get_latest_plan_subscription


class APIPostPlanSubscriptionTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_login = {
            'email': 'email@jurema.la',
            'password': 'password',
        }

        cls.data_user = {
            **cls.data_login,
            'city': 'Cidade',
            'full_name': 'Nome Completo',
            'gender': 'm',
            'state': 'UF',
            'sector': 'private'
        }

        cls.user = User.objects.create_user(**cls.data_user)
        cls.user.save()

    def test_single_trial_end_task(self):
        task = SingleTrialEndTask(user=self.user)
        task()
        self.assertEquals(len(mail.outbox), 1)

    def test_daily_setup_trial_end_task(self):
        dummy_users = []

        def dummy(**kwargs):
            dummy_users.append(kwargs.get('user'))

        task = DailySetupTrialEndTask(subtask=dummy)
        task()

        self.assertEquals(dummy_users, [])

        user_subscription: PlanSubscription = user_get_latest_plan_subscription(
            user=self.user)
        trial_end = timezone.datetime.today() + timezone.timedelta(days=1)
        user_subscription.trial_end_at = trial_end.date()
        user_subscription.save()

        task = DailySetupTrialEndTask(subtask=dummy)
        task()

        self.assertEquals(dummy_users, [self.user])
