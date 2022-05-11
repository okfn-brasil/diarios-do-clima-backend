from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from ..serializers import (
    AddressSerializer,
)

from ..models import (
    Address,
)


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
