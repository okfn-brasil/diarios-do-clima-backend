from .models import User
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus


def user_get_current_plan_subscription(
        user: User,
) -> PlanSubscription:
    try:
        plan_subscription_status: PlanSubscriptionStatus = PlanSubscriptionStatus.objects.filter(
            plan_subscription__user=user
        ).latest('created_at')
        plan_subscription = plan_subscription_status.plan_subscription
    except PlanSubscriptionStatus.DoesNotExist:
        plan_subscription = PlanSubscription.objects.filter(
            user=user).latest('created_at')

    return plan_subscription
