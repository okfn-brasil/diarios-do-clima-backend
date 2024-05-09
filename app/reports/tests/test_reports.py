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
            'email': 'email@diariosdoclima.org.br',
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

        self.public_report = Report(
            title='report 1',
            description='report 1',
            is_public=True,
            file=file_mock,
        )

        self.public_report.save()

    def setUpReportsPrivate(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test2.jpg'

        self.private_report = Report(
            title='report 2',
            description='report 2',
            is_public=False,
            file=file_mock,
        )

        self.private_report.save()

    def setUpReportsPrivateForUser(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test3.jpg'

        self.user_report = Report(
            title='report 3',
            description='report 3',
            is_public=False,
            file=file_mock,
        )
        self.user_report.save()

        report_access = ReportUserAccess(
            report=self.user_report,
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

    def test_get_one_public(self):
        self.login()
        self.setUpReportsPublic()

        response = self.client.get(
            reverse('reports', kwargs={'pk': str(self.public_report.pk)}),
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data: dict = response.json()
        id = data.get('id', None)
        self.assertNotEquals(id, None)
        self.assertEquals(id, str(self.public_report.pk))

    def test_get_one_private_report(self):
        self.login()
        self.setUpReportsPublic()
        self.setUpReportsPrivate()

        response = self.client.get(
            reverse('reports', kwargs={'pk': str(self.private_report.pk)}),
        )

        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        data: dict = response.json()
        self.assertEquals(data, {'detail': 'Não encontrado.'})

    def test_get_one_user_report_private(self):
        self.login()
        self.setUpReportsPublic()
        self.setUpReportsPrivate()
        self.setUpReportsPrivateForUser()

        response = self.client.get(
            reverse('reports', kwargs={'pk': str(self.user_report.pk)}),
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        data: dict = response.json()
        id = data.get('id', None)
        self.assertNotEquals(id, None)
        self.assertEquals(id, str(self.user_report.pk))
