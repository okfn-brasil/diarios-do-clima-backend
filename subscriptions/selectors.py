from .models import PlanSubscription, PlanSubscriptionStatus


def plan_subscription_get_latest_status(plan_subscription: PlanSubscription) -> PlanSubscriptionStatus:
    return PlanSubscriptionStatus.objects.filter(plan_subscription=plan_subscription).latest('created_at')
