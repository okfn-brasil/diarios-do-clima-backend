from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from ..models import PlanSubscription, PlanSubscriptionStatus, Plan
from ..serializers import PlanSubscriptionSerializer
from ..selectors import user_get_latest_plan_subscription
from billing.selectors import user_get_current_credit_card
from libs.services import services
from libs.pagseguro import PagSeguroApiABC
from libs.pagseguro.serializers import SubscribeSerializer
from libs.get_client_ip import get_client_ip


class PlanSubscriptionApiView(CreateAPIView):
    serializer_class = PlanSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def previous_plan_subscription_cancel(self) -> None:
        try:
            previous_plan_subscription = user_get_latest_plan_subscription(
                user=self.request.user,
            )
        except PlanSubscription.DoesNotExist:
            return

        previous_plan: Plan = previous_plan_subscription.plan

        if previous_plan.to_charge():
            pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
            pag_seguro_api.subscription_cancel(
                previous_plan_subscription.pagseguro_code
            )
        else:
            plan_subscription_cancelled_status = PlanSubscriptionStatus(
                plan_subscription=previous_plan_subscription,
                pagseguro_data=PlanSubscriptionStatus.DATA_CANCELLED,
            )
            plan_subscription_cancelled_status.save()

    def new_plan_subscription_create(self, plan_subscription: PlanSubscription) -> None:

        plan: Plan = plan_subscription.plan

        if not plan.to_charge():
            plan_subscription_status = PlanSubscriptionStatus(
                plan_subscription=plan_subscription,
                pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
            )
            plan_subscription_status.save()
            return

        subscribe_serializer = SubscribeSerializer(
            user=self.request.user,
            plan_subscription=plan_subscription,
            credit_card=user_get_current_credit_card(
                user=self.request.user
            ),
            ip=get_client_ip(self.request)
        )

        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)

        code = pag_seguro_api.subscription_create(
            serializer=subscribe_serializer
        )
        plan_subscription.pagseguro_code = code

    def set_trial_end(self, plan_subscription: PlanSubscription) -> None:
        plan: Plan = plan_subscription.plan
        if not plan.to_charge():
            return
        today = timezone.datetime.today()
        time_delta = timezone.timedelta(days=plan.trial_days)
        trial_end_at = today + time_delta
        plan_subscription.trial_end_at = trial_end_at

    def perform_create(self, serializer):
        with transaction.atomic():
            self.previous_plan_subscription_cancel()
            plan_subscription = serializer.save(user=self.request.user)
            self.set_trial_end(plan_subscription=plan_subscription)
            self.new_plan_subscription_create(
                plan_subscription=plan_subscription,
            )
            plan_subscription.save()
