from unittest import mock
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from plans.models import Plan
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus
from subscriptions.selectors import (
    plan_subscription_get_latest_status,
    user_get_latest_plan_subscription,
)
from libs.services import services
from libs.pagseguro import PagSeguroApiABC, PreApprovalNotification
from django.utils import timezone


class APIPlanSubscriptionNotificationsWebhookTestCase(APITestCase):

    @classmethod
    def setUpUser(cls):
        cls.data_login = {
            'email': 'email@diariosdoclima.org.br',
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

    @classmethod
    def setUpPlan(cls):
        plan = Plan(
            title="Outro Gratis",
            html="<p>Outro Free Plan</p>"
        )
        plan.save()
        plan_subscription = PlanSubscription(
            user=cls.user,
            plan=plan,
        )
        plan_subscription.save()
        plan_subscription_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
        )
        plan_subscription_status.save()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.setUpUser()
        cls.setUpPlan()

    def test_webhook_created_new_status(self):
        notification_type = 'preApproval'
        notification_code = 'notification_code'
        notification_date = '2022-04-29T15:53:17-03:00'
        subscription_code = 'subscription_code'

        plan_subscription = user_get_latest_plan_subscription(user=self.user)
        plan_subscription.pagseguro_code = subscription_code
        plan_subscription.save()

        self.assertNotEquals(
            str(plan_subscription.plan.pk),
            settings.DIARIOS_DEFAULT_FREE_PLAN_ID,
        )

        data = {
            'notificationType': notification_type,
            'notificationCode': notification_code,
        }

        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        PagSeguroApiMock.subscription_get_notification.return_value = PreApprovalNotification(
            code=subscription_code,
            date=notification_date,
            status=PlanSubscriptionStatus.DATA_CANCELLED,
        )

        services.register(PagSeguroApiABC, PagSeguroApiMock)

        response = self.client.post(
            reverse('notifications'),
            data,
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        latest_plan_subscription_status: PlanSubscriptionStatus = plan_subscription_get_latest_status(
            plan_subscription=plan_subscription
        )

        self.assertEquals(
            latest_plan_subscription_status.pagseguro_data,
            PlanSubscriptionStatus.DATA_CANCELLED,
        )

        date = timezone.datetime.strptime(
            notification_date,
            '%Y-%m-%dT%H:%M:%S%z',
        )

        self.assertEquals(
            latest_plan_subscription_status.pagseguro_notification_date,
            date,
        )

        curent_plan_subscription = user_get_latest_plan_subscription(user=self.user)

        self.assertEquals(
            str(curent_plan_subscription.plan.pk),
            settings.DIARIOS_DEFAULT_FREE_PLAN_ID,
        )
