from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import User


class APIUserCreateTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.data = {
            'email': 'email@jurema.la',
            'password': 'password',
            'city': 'Cidade',
            'full_name': 'Nome Completo',
            'gender': 'm',
            'state': 'UF',
            'sector': 'private'
        }

    def test_create_user(self):
        response = self.client.post(reverse('users'), self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_create_user_email_required(self):
        data = {
            **self.data,
        }

        del data['email']

        response = self.client.post(reverse('users'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_create_user_password_required(self):
        data = {
            **self.data,
        }
        
        del data['password']

        response = self.client.post(reverse('users'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
