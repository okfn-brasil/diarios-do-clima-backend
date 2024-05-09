from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from libs.services import services
from libs.pagseguro import PagSeguroApiABC
from unittest import mock


class APIUserMeGetTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()        
        cls.client = APIClient()

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
        user = User.objects.create_user(**cls.data_user)
        user.save()

    def test_pagseguro_session_get(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )
        self.assertEqual(response.status_code, 200)

        access: str = response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        self.session_id = 'mock_session_id'
        PagSeguroApiMock.get_session.return_value = self.session_id

        services.register(PagSeguroApiABC, PagSeguroApiMock)
        response = self.client.get(reverse('session'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        session_id = data['session']
        self.assertEqual(self.session_id, session_id)
