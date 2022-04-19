from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..serializers import PlanSerializer
from ..actions import get_or_create_default_plan


class APIPlanGetListTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

    def test_get_empty_list(self):
        response = self.client.get(
            reverse('plans'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data)
        empty = {'count': 0, 'next': None, 'previous': None, 'results': []}
        self.assertEquals(data, empty)

    def test_get_list_default_plan(self):
        plan = get_or_create_default_plan()
        response = self.client.get(
            reverse('plans'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNotNone(data)
        plan_serializer = PlanSerializer(plan)
        result = {'count': 1, 'next': None, 'previous': None, 'results': [
            plan_serializer.data,
        ]}
        self.assertEquals(data, result)
