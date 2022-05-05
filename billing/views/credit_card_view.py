from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from ..serializers import (
    CreditCardSerializer,
)

from ..models import (
    CreditCard,
)

from libs.pagseguro import PagSeguroApiABC
from libs.services import services


class CreditCardView(ListAPIView, CreateAPIView):
    serializer_class = CreditCardSerializer
    queryset = CreditCard.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        serializer.save(user=self.request.user)
