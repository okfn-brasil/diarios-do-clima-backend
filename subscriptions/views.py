from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from .models import PlanSubscriptionStatus
from .serializers import PlanSubscriptionSerializer


class PlanSubscriptionApiView(CreateAPIView):
    serializer_class = PlanSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        plan_subscription = serializer.save(user=self.request.user)
        plan_subscription.save()
        plan_subscription_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
        )
        plan_subscription_status.save()
