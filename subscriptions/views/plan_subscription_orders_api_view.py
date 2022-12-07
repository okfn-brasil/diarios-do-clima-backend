from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import PlanSubscription
from libs.services import services
from libs.pagseguro import PagSeguroApiABC


class PlanSubscriptionOrdersApiView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        plan_subscription = PlanSubscription.objects.get(pk=pk)
        pag_seguro: PagSeguroApiABC = services.get(PagSeguroApiABC)

        if not plan_subscription.pagseguro_code:
            return Response({"plan_subscription": ["this subscription does not have a code"]}, status=status.HTTP_400_BAD_REQUEST)

        data = pag_seguro.subscription_orders(plan_subscription.pagseguro_code)
        return Response(data)
