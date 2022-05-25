from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from plans.models import Plan
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus
from libs.services import services
from libs.querido_diario import QueridoDiarioABC
from libs.querido_diario.serializers import GazettesResult
from unittest import mock
from libs.utils.datetime import datetime_to_date_str_diario


class APIGazettesTestCase(APITestCase):

    @classmethod
    def setUpUser(cls):
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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.setUpUser()
        cls.QueridoDiarioMock = mock.MagicMock(spec=QueridoDiarioABC)
        services.register(QueridoDiarioABC, cls.QueridoDiarioMock)
        cls.QueridoDiarioMock.gazettes.return_value = GazettesResult(
            total_gazettes=0,
            gazettes=[],
        )

    def login(self):
        login_response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access: str = login_response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

    def setup_user_pro_plan(self):
        plan = Plan(
            title="Pro",
            html="<p>p</p>",
            pagseguro_plan_id="code",
        )
        plan.save()

        plan_subscription = PlanSubscription(
            user=self.user,
            plan=plan,
            pagseguro_code='code',
        )
        plan_subscription.save()
        plan_subscription_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,

        )
        plan_subscription_status.save()

    def test_gazettes_get_without_user(self):
        response = self.client.get(
            reverse('gazettes'),
        )
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_gazettes_get_with_user(self):
        self.login()
        response = self.client.get(
            reverse('gazettes'),
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_gazettes_get_since_query_with_non_pro_user(self):
        self.login()
        today = timezone.now()
        delta = timezone.timedelta(days=90)
        diff: timezone.datetime = today - delta
        date_str = datetime_to_date_str_diario(date=diff)
        response = self.client.get(
            reverse('gazettes') + f'?since={date_str}',
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_gazettes_get_pro_since_query_with_non_pro_user(self):
        self.login()
        response = self.client.get(
            reverse('gazettes') + '?since=2015-01-01',
        )
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        since = data.get('since', None)
        self.assertEquals(since, 'data somente disponivel para plano pro')

    def test_gazettes_get_pro_subtheme_query_with_non_pro_user(self):
        self.login()
        response = self.client.get(
            reverse('gazettes') + '?subtheme=sub1&subtheme=sub2',
        )
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        subtheme = data.get('subtheme', None)
        self.assertEquals(
            subtheme, 'sub temas somente disponiveis para plano pro')

    def test_gazettes_get_pro_query_with_pro_user(self):
        self.login()
        self.setup_user_pro_plan()
        response = self.client.get(
            reverse('gazettes') +
            '?since=2015-01-01&subtheme=sub1&subtheme=sub2',
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
