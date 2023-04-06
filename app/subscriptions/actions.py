from django.conf import settings
from accounts.models import User
from plans.models import Plan
from plans.actions import (
    create_user_default_plan_subscription,
)
from .selectors import user_get_latest_plan_subscription
from .models import PlanSubscription


def user_plan_subscription_cancel(user: User):
    plan_subscription: PlanSubscription = user_get_latest_plan_subscription(
        user=user
    )
    plan: Plan = plan_subscription.plan

    if str(plan.id) == settings.DIARIO_DEFAULT_FREE_PLAN_ID:
        raise Exception("can not cancel default free plan")

    create_user_default_plan_subscription(
        user=user,
    )
