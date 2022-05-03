from uuid import uuid4
from unittest import mock
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from plans.models import Plan
from subscriptions.models import PlanSubscription
from libs.services import services
from libs.pagseguro import PagSeguroApiABC
from billing.models import Phone, Address, CreditCard


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

        cls.user = User.objects.create_user(**cls.data_user)
        cls.user.save()

        cls.plan = Plan(
            id=uuid4(),
            title="Outro Gratis",
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

    def test_pro_plan(self):
        pag_seguro_id = 'pag_seguro_id'
        plan = Plan(
            title="pro teste",
            html="<p>teste</p>",            
            pagseguro_plan_id=pag_seguro_id,
        )
        plan.save()

        phone = Phone(
            user=self.user,
            area_code='63',
            number='999999999',
        )
        phone.save()

        credit_card = CreditCard(
            user=self.user,
            token="a34s",
            last_four_digits="4423",
            exp_month="12",
            exp_year="2030",
            holder_name="Paulo",
            holder_birth_date="1992-08-06",
            cpf="0000000"
        )
        credit_card.save()

        address = Address(
            user=self.user,
            street="a",
            number="4",
            complement="b",
            district="c",
            city="d",
            state="e",
            country="BRA",
            postal_code="234234"
        )
        address.save()

        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        subscription_code = 'mock_sub_code'
        PagSeguroApiMock.subscribe.return_value = subscription_code
        services.register(PagSeguroApiABC, PagSeguroApiMock)

        login_response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access: str = login_response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

        subscriptions_data = {
            'plan': plan.id,
        }

        subscriptions_response = self.client.post(
            reverse('subscriptions'),
            subscriptions_data,
        )

        self.assertEqual(
            subscriptions_response.status_code,
            status.HTTP_201_CREATED,
        )

        sub: PlanSubscription = PlanSubscription.objects.filter(
            user=self.user).latest('created_at')

        self.assertEqual(sub.pagseguro_code, subscription_code)
