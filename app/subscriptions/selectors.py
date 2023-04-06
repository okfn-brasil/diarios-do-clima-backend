from accounts.models import User
from .models import PlanSubscription, PlanSubscriptionStatus


def plan_subscription_get_latest_status(plan_subscription: PlanSubscription) -> PlanSubscriptionStatus:
    return PlanSubscriptionStatus.objects.filter(plan_subscription=plan_subscription).latest('created_at')


def user_get_latest_plan_subscription(user: User) -> PlanSubscription:
    return PlanSubscription.objects.filter(user=user).latest('created_at')
