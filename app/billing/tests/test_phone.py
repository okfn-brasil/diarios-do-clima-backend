from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User, Phone


class APIPhoneTestCase(APITestCase):

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
        self.area_code = '63'
        self.number = '999999999'
        self.data = {
            'area_code': self.area_code,
            'number': self.number,
        }
        response = self.client.post(reverse('phone'), data=self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_post_new_phone(self):
        self.login()
        self.create_phone()
        self.assertEquals(self.user.phone.area_code, self.area_code)
        self.assertEquals(self.user.phone.number, self.number)

    def test_get_user_phone(self):
        self.login()
        self.create_phone()
        response = self.client.get(reverse('phone'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEquals(response_data, self.data)

    def test_edit_patch_user_phone(self):
        self.login()
        self.create_phone()
        data = {'area_code': '54', }
        response = self.client.patch(reverse('phone'), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        phone = Phone.objects.get(user=self.user)
        self.assertEquals(phone.area_code, data['area_code'])

    def test_edit_put_user_phone(self):
        self.login()
        self.create_phone()
        data = {'area_code': '54', 'number': '000'}
        response = self.client.put(reverse('phone'), data=data)
        phone = Phone.objects.get(user=self.user)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(phone.area_code, data['area_code'])
        self.assertEquals(phone.number, data['number'])

    def test_edit_patch_no_phone(self):
        self.login()
        data = {'area_code': '54', }
        response = self.client.patch(reverse('phone'), data=data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_put_no_phone(self):        
        self.login()
        data = {'area_code': '54', 'number': '000'}
        response = self.client.put(reverse('phone'), data=data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_no_phone(self):
        self.login()
        response = self.client.get(reverse('phone'))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
