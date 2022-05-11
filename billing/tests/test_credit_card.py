from unittest import mock
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User, CreditCard
from ..selectors import user_get_current_credit_card
from libs.services import services
from libs.pagseguro import PagSeguroApiABC


class APICreditCardTestCase(APITestCase):

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

    def login(self):
        login_response = self.client.post(
            reverse('token_obtain_pair'),
            self.data_login,
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access: str = login_response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)

    def create_phone(self):
        data = {
            'area_code': '63',
            'number': '999999999',
        }
        response = self.client.post(reverse('phone'), data=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def create_address(self):
        data = {
            "street": "a",
            "number": "4",
            "complement": "b",
            "district": "c",
            "city": "d",
            "state": "e",
            "country": "BRA",
            "postal_code": "234234",
        }
        response = self.client.post(reverse('address'), data=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def create_credit_card(self):
        self.create_phone()
        self.create_address()
        self.token = "cf61f3f086b04673854a53091e59a9bb"
        self.last_four_digits = "111"
        self.exp_month = "12"
        self.exp_year = "2030"
        self.holder_name = "Paulo"
        self.holder_birth_date = "1992-08-06"
        self.cpf = "01234567890"

        self.data = {
            "token": self.token,
            "last_four_digits": self.last_four_digits,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "holder_name": self.holder_name,
            "holder_birth_date": self.holder_birth_date,
            "cpf": self.cpf,
        }
        response = self.client.post(reverse('credit_card'), data=self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_post_new_credit_card(self):
        self.login()
        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        services.register(PagSeguroApiABC, PagSeguroApiMock)
        self.create_credit_card()
        credit_card: CreditCard = user_get_current_credit_card(user=self.user)
        self.assertEquals(credit_card.token, self.token)
        self.assertEquals(credit_card.cpf, self.cpf)

    def test_get_user_credit_card(self):
        self.login()
        PagSeguroApiMock = mock.Mock(spec=PagSeguroApiABC)
        services.register(PagSeguroApiABC, PagSeguroApiMock)
        self.create_credit_card()
        response = self.client.get(reverse('credit_card'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()        
        self.assertEquals(response_data['count'], 1)

    def test_get_no_credit_card(self):
        self.login()
        response = self.client.get(reverse('credit_card'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEquals(response_data['count'], 0)
