from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Plan
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus
User = get_user_model()


def get_or_create_default_plan():
    try:
        plan = Plan.objects.get(pk=settings.DIARIO_DEFAULT_FREE_PLAN_ID)
    except Plan.DoesNotExist:
        plan = Plan(
            id=settings.DIARIO_DEFAULT_FREE_PLAN_ID,
            title="Gratis",
            price=0,
            html="<p>Default Free Plan</p>"
        )
        plan.save()

    return plan


def create_user_default_plan_subscription(user: User, plan: Plan):
    plan_subscription = PlanSubscription(
        user=user,
        plan=plan,
    )
    plan_subscription.save()
    plan_subscription_status = PlanSubscriptionStatus(
        plan_subscription=plan_subscription,
        pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
    )
    plan_subscription_status.save()
