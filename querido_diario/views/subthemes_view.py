from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from libs.services import services
from libs.querido_diario import QueridoDiarioABC


class SubThemesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        querido_diario: QueridoDiarioABC = services.get(QueridoDiarioABC)
        data = querido_diario.subthemes()
        return Response(data=data, status=200)
