from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from accounts.models import User
from django.urls import reverse
from ..models import Report, ReportUserAccess

from unittest import mock
from django.core.files import File


class APIReportsTestCase(APITestCase):

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
            'sector': 'private',
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

    def setUpReportsPublic(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.jpg'

        report = Report(
            title='report 1',
            description='report 1',
            is_public=True,
            file=file_mock,
        )

        report.save()

    def setUpReportsPrivate(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test2.jpg'

        report = Report(
            title='report 2',
            description='report 2',
            is_public=False,
            file=file_mock,
        )

        report.save()

    def setUpReportsPrivateForUser(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test3.jpg'

        report = Report(
            title='report 3',
            description='report 3',
            is_public=False,
            file=file_mock,
        )
        report.save()

        report_access = ReportUserAccess(
            report=report,
            user=self.user,
        )
        report_access.save()

    def test_get_public_reports(self):
        self.login()
        self.setUpReportsPublic()

        response = self.client.get(reverse('reports_public'),)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data: dict = response.json()
        results = data.get('results', None)
        self.assertNotEquals(results, None)
        self.assertEquals(len(results), 1)

    def test_user_with_no_private_reports(self):
        self.login()
        self.setUpReportsPublic()
        self.setUpReportsPrivate()

        response = self.client.get(reverse('reports_private'),)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data: dict = response.json()
        results = data.get('results', None)
        self.assertNotEquals(results, None)
        self.assertEquals(len(results), 0)

    def test_user_with_some_private_reports(self):
        self.login()
        self.setUpReportsPublic()
        self.setUpReportsPrivate()
        self.setUpReportsPrivateForUser()

        response = self.client.get(reverse('reports_private'),)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data: dict = response.json()
        results = data.get('results', None)
        self.assertNotEquals(results, None)
        self.assertEquals(len(results), 1)
