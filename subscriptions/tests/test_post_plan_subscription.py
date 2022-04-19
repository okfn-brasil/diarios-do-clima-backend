from uuid import uuid4
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from plans.models import Plan


class APIPostPlanSubscriptionTestCase(APITestCase):

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

        user = User.objects.create_user(**cls.data_user)
        user.save()

        cls.plan = Plan(
            id=uuid4(),
            title="Outro Gratis",
            price=0,
            html="<p>Outro Free Plan</p>"
        )
        cls.plan.save()

    def test_post_free_plan_subscription(self):
        login_response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access: str = login_response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

        me_response_before = self.client.get(reverse('users_me'))

        self.assertEqual(me_response_before.status_code, status.HTTP_200_OK)

        data = me_response_before.json()
        plan_subscription = data.get('plan_subscription', None)
        self.assertIsNotNone(plan_subscription)
        plan = plan_subscription.get('plan', None)
        self.assertIsNotNone(plan)
        user_plan_id = plan.get('id', None)

        self.assertEqual(
            user_plan_id, settings.DIARIO_DEFAULT_FREE_PLAN_ID
        )

        subscriptions_data = {
            'plan': self.plan.id,
        }

        subscriptions_response = self.client.post(
            reverse('subscriptions'),
            subscriptions_data,
        )

        self.assertEqual(
            subscriptions_response.status_code,
            status.HTTP_201_CREATED,
        )

        me_response_after = self.client.get(reverse('users_me'))

        self.assertEqual(me_response_after.status_code, status.HTTP_200_OK)

        data = me_response_after.json()
        plan_subscription = data.get('plan_subscription', None)
        self.assertIsNotNone(plan_subscription)
        plan = plan_subscription.get('plan', None)
        self.assertIsNotNone(plan)
        user_plan_id = plan.get('id', None)

        self.assertEqual(user_plan_id, str(self.plan.id))
