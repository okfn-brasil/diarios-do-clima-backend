import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .serializers import (
    PhoneSerializer,
    AddressSerializer,
    CreditCardSerializer,
)

from .models import (
    Phone,
    Address,
    CreditCard,
)


class PhoneView(RetrieveUpdateAPIView, CreateAPIView):
    serializer_class = PhoneSerializer
    queryset = Phone.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        try:
            return self.request.user.phone
        except ObjectDoesNotExist:
            raise NotFound()


class AddressView(RetrieveUpdateAPIView, CreateAPIView):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        try:
            return self.request.user.address
        except ObjectDoesNotExist:
            raise NotFound()


class CreditCardView(RetrieveUpdateAPIView, CreateAPIView):
    serializer_class = CreditCardSerializer
    queryset = CreditCard.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        try:
            return self.request.user.creditcard
        except ObjectDoesNotExist:
            raise NotFound()


class PagSeguroSession(APIView):    
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        url = f"https://ws.sandbox.pagseguro.uol.com.br/v2/sessions?email={settings.DIARIO_PAGSEGURO_EMAIL}&token={settings.DIARIO_PAGSEGURO_TOKEN}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data={})
        session = ET.fromstring(response.text)
        id = session.find('id')
        return Response(
            data={
                'session': id.text,
            }
        )
