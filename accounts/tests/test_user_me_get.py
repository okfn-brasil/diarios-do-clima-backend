from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User


class APIUserMeGetTestCase(APITestCase):

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

    def test_login_get_users_me_no_acces_token(self):
        response = self.client.get(reverse('users_me'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_get_users_me(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access: str = response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

        self.assertIsNotNone(access)

        response = self.client.get(reverse('users_me'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()        
        plan_subscription = data.get('plan_subscription', None)
        self.assertIsNotNone(plan_subscription)

        plan = plan_subscription.get('plan', None)
        self.assertIsNotNone(plan)
        
        plan_id = plan.get('id', None)
        self.assertEquals(plan_id, settings.DIARIO_DEFAULT_FREE_PLAN_ID)

