from unittest import mock
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus
from subscriptions.selectors import plan_subscription_get_latest_status
from libs.services import services
from libs.pagseguro import PagSeguroApiABC, PreApprovalNotification


class APIPlanSubscriptionNotificationsWebhookTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
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

    def test_webhook_created_new_status(self):
        notification_type = 'preApproval'
        notification_code = 'notification_code'
        subscription_code = 'subscription_code'

        plan_subscription = PlanSubscription.objects.get(
            user=self.user,
        )
        plan_subscription.pagseguro_code = subscription_code
        plan_subscription.save()

        data = {
            'notificationType': notification_type,
            'notificationCode': notification_code,
        }

        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        PagSeguroApiMock.pre_approvals_get_notification.return_value = PreApprovalNotification(
            code=subscription_code,
            date="2022-04-29T15:53:17-03:00",
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
