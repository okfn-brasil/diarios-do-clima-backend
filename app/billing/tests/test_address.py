from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User, Address


class APIAddressTestCase(APITestCase):

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

    def create_address(self):
        self.street = "a"
        self.number = "4"
        self.complement = "b"
        self.district = "c"
        self.city = "d"
        self.state = "e"
        self.country = "BRA"
        self.postal_code = "234234"

        self.data = {
            "street": self.street,
            "number": self.number,
            "complement": self.complement,
            "district": self.district,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
        }
        response = self.client.post(reverse('address'), data=self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(self.user.address.street, self.street)
        self.assertEquals(self.user.address.number, self.number)
        self.assertEquals(self.user.address.complement, self.complement)
        self.assertEquals(self.user.address.district, self.district)
        self.assertEquals(self.user.address.city, self.city)
        self.assertEquals(self.user.address.state, self.state)
        self.assertEquals(self.user.address.country, self.country)
        self.assertEquals(self.user.address.postal_code, self.postal_code)

    def test_post_new_address(self):
        self.login()
        self.create_address()

        response = self.client.get(reverse('address'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEquals(response_data, self.data)

    def test_get_user_address(self):
        self.login()
        self.create_address()
        response = self.client.get(reverse('address'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEquals(response_data, self.data)

    def test_edit_patch_user_address(self):
        self.login()
        self.create_address()
        data = {'number': '54', }
        response = self.client.patch(reverse('address'), data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        address = Address.objects.get(user=self.user)
        self.assertEquals(address.number, data['number'])

    def test_edit_put_user_address(self):
        self.login()
        self.create_address()

        street = "abd"
        number = "44"
        complement = "b"
        district = "cg"
        city = "gd"
        state = "ie"
        country = "BRA"
        postal_code = "2344"

        data = {
            "street": street,
            "number": number,
            "complement": complement,
            "district": district,
            "city": city,
            "state": state,
            "country": country,
            "postal_code": postal_code,
        }
        response = self.client.put(reverse('address'), data=data)
        address = Address.objects.get(user=self.user)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(address.street, data['street'])
        self.assertEquals(address.number, data['number'])
        self.assertEquals(address.complement, data['complement'])
        self.assertEquals(address.district, data['district'])
        self.assertEquals(address.city, data['city'])
        self.assertEquals(address.state, data['state'])
        self.assertEquals(address.country, data['country'])
        self.assertEquals(address.postal_code, data['postal_code'])

    def test_edit_patch_address(self):
        self.login()
        street = "bb"
        number = "45"
        data = {
            "street": street,
            "number": number,
        }
        response = self.client.patch(reverse('address'), data=data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_put_address(self):
        self.login()

        street = "abd"
        number = "44"
        complement = "b"
        district = "cg"
        city = "gd"
        state = "et"
        country = "BRA"
        postal_code = "2344"

        data = {
            "street": street,
            "number": number,
            "complement": complement,
            "district": district,
            "city": city,
            "state": state,
            "country": country,
            "postal_code": postal_code,
        }
        response = self.client.put(reverse('address'), data=data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_no_address(self):
        self.login()
        response = self.client.get(reverse('address'))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
