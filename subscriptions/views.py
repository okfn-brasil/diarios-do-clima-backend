from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from .models import PlanSubscriptionStatus, Plan
from .serializers import PlanSubscriptionSerializer
from libs.services import services
from libs.pagseguro import PagSeguroApiABC
from libs.pagseguro.serializers import SubscribeSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PlanSubscriptionApiView(CreateAPIView):
    serializer_class = PlanSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        with transaction.atomic():
            plan_subscription = serializer.save(user=self.request.user)
            plan_subscription.save()
            plan_subscription_status = PlanSubscriptionStatus(
                plan_subscription=plan_subscription,
                pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
            )
            plan_subscription_status.save()
            plan: Plan = plan_subscription.plan

            if not plan.to_charge():
                return

            pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
            subscribe_serializer = SubscribeSerializer(
                user=self.request.user,
                plan_subscription=plan_subscription,
                ip=get_client_ip(self.request)
            )
            code = pag_seguro_api.subscribe(serializer=subscribe_serializer)
            plan_subscription.pagseguro_code = code
            plan_subscription.save()
