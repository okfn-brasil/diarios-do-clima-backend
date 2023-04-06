from unittest import mock
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from plans.models import Plan
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus
from subscriptions.selectors import (    
    user_get_latest_plan_subscription,
)
from libs.services import services
from libs.pagseguro import PagSeguroApiABC, PreApprovalNotification


class APIPlanSubscriptionCancelTestCase(APITestCase):

    @classmethod
    def setUpUser(cls):
        cls.data_login = {
            'email': 'email@diariodoclima.org.br',
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
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.setUpUser()

    def login(self):
        login_response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access: str = login_response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

    def setUpPlanLocal(self):
        plan = Plan(
            title="Outro Gratis",
            html="<p>Outro Free Plan</p>"
        )
        plan.save()
        plan_subscription = PlanSubscription(
            user=self.user,
            plan=plan,
        )
        plan_subscription.save()
        plan_subscription_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
        )
        plan_subscription_status.save()

    def setUpPlanPagseguro(self):
        self.subscription_code = 'subscription_code'
        plan = Plan(
            title="Outro Gratis",
            html="<p>Outro Free Plan</p>",
            pagseguro_plan_id='code',
            trial_days=7,
        )
        plan.save()
        plan_subscription = PlanSubscription(
            user=self.user,
            plan=plan,
            pagseguro_code=self.subscription_code,
        )
        plan_subscription.save()
        plan_subscription_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
        )
        plan_subscription_status.save()

    def test_cancel_local_plan_subscription(self):
        self.login()
        self.setUpPlanLocal()

        plan_subscription = user_get_latest_plan_subscription(
            user=self.user)

        self.assertNotEquals(
            str(plan_subscription.plan.pk),
            settings.DIARIO_DEFAULT_FREE_PLAN_ID,
        )

        response = self.client.post(
            reverse('subscriptions_cancel'),
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        plan_subscription = user_get_latest_plan_subscription(
            user=self.user
        )

        self.assertEquals(
            str(plan_subscription.plan.pk),
            settings.DIARIO_DEFAULT_FREE_PLAN_ID,
        )

    def test_cancel_pagseguro_plan_subscription(self):
        self.login()
        self.setUpPlanPagseguro()

        start_plan_subscription = user_get_latest_plan_subscription(
            user=self.user)

        self.assertNotEquals(
            str(start_plan_subscription.plan.pk),
            settings.DIARIO_DEFAULT_FREE_PLAN_ID,
        )

        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        services.register(PagSeguroApiABC, PagSeguroApiMock)

        response = self.client.post(
            reverse('subscriptions_cancel'),
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        end_plan_subscription = user_get_latest_plan_subscription(
            user=self.user)

        self.assertEquals(
            start_plan_subscription.pk,
            end_plan_subscription.pk,
        )

        notification_type = 'preApproval'
        notification_code = 'notification_code'
        notification_date = '2022-04-29T15:53:17-03:00'

        data = {
            'notificationType': notification_type,
            'notificationCode': notification_code,
        }
        PagSeguroApiMock.subscription_get_notification.return_value = PreApprovalNotification(
            code=self.subscription_code,
            date=notification_date,
            status=PlanSubscriptionStatus.DATA_CANCELLED,
        )

        response = self.client.post(
            reverse('notifications'),
            data,
        )

        curent_plan_subscription = user_get_latest_plan_subscription(user=self.user)

        self.assertEquals(
            str(curent_plan_subscription.plan.pk),
            settings.DIARIO_DEFAULT_FREE_PLAN_ID,
        )
