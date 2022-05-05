from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from libs.pagseguro import PagSeguroApiABC
from libs.services import services


class PagSeguroSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        session = pag_seguro_api.get_session()

        return Response(
            data={
                'session': session,
            }
        )
