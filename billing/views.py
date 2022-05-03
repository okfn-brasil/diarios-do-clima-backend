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

from libs.pagseguro import PagSeguroApiABC
from libs.services import services


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
        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        session = pag_seguro_api.get_session()

        return Response(
            data={
                'session': session,
            }
        )
