from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from plans.actions import create_user_default_plan_subscription
from ..models import PlanSubscription, PlanSubscriptionStatus, Plan
from ..selectors import user_get_latest_plan_subscription
from libs.services import services
from libs.pagseguro import PagSeguroApiABC


class PlanSubscriptionCancelAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def pagseguro_plan_subscription_cancel(self, plan_subscription: PlanSubscription) -> None:
        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        pag_seguro_api.subscription_cancel(
            subscription_code=plan_subscription.pagseguro_code
        )

    def local_only_plan_subscription_cancel(self, plan_subscription: PlanSubscription) -> None:
        cancel_status = PlanSubscriptionStatus(
            plan_subscription=plan_subscription,
            pagseguro_data=PlanSubscriptionStatus.DATA_CANCELLED,
        )
        cancel_status.save()
        create_user_default_plan_subscription(user=self.request.user)

    def post(self, request, *args, **kwargs):
        plan_subscription: PlanSubscription = user_get_latest_plan_subscription(
            user=self.request.user,
        )
        plan: Plan = plan_subscription.plan

        if str(plan.id) == settings.DIARIOS_DEFAULT_FREE_PLAN_ID:
            raise Exception("can not cancel default free plan")

        if plan.to_charge():
            self.pagseguro_plan_subscription_cancel(
                plan_subscription=plan_subscription,
            )
        else:
            self.local_only_plan_subscription_cancel(
                plan_subscription=plan_subscription,
            )

        return Response()
