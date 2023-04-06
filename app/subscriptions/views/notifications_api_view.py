from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import PlanSubscription, PlanSubscriptionStatus
from ..actions import user_plan_subscription_cancel
from ..selectors import user_get_latest_plan_subscription
from libs.services import services
from libs.pagseguro import PagSeguroApiABC, PreApprovalNotification
from django.utils import timezone


class NotificationsApiView(APIView):
    notification_type = 'preApproval'

    def plan_subscription_status_update(self, notification_code: str):
        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)

        self.notification: PreApprovalNotification = pag_seguro_api.subscription_get_notification(
            notification_code=notification_code
        )

        self.plan_subscription = PlanSubscription.objects.get(
            pagseguro_code=self.notification.code,
        )
        pagseguro_notification_date = timezone.datetime.strptime(
            self.notification.date,
            '%Y-%m-%dT%H:%M:%S%z',
        )

        try:
            PlanSubscriptionStatus.objects.get(
                pagseguro_notification_code=notification_code)
        except PlanSubscriptionStatus.DoesNotExist:
            plan_subscription_status = PlanSubscriptionStatus(
                plan_subscription=self.plan_subscription,
                pagseguro_data=self.notification.status,
                pagseguro_notification_code=notification_code,
                pagseguro_notification_date=pagseguro_notification_date
            )
            plan_subscription_status.save()

    def plan_subscription_cancel(self):
        current_plan_subscription = user_get_latest_plan_subscription(
            user=self.plan_subscription.user
        )
        if current_plan_subscription.pk == self.plan_subscription.pk:
            user_plan_subscription_cancel(
                user=self.plan_subscription.user,
            )

    def post(self, request, *args, **kwargs):
        notification_code = request.POST.get('notificationCode')
        notification_type = request.POST.get('notificationType')

        if notification_type != self.notification_type:
            return Response()

        self.plan_subscription_status_update(
            notification_code=notification_code
        )

        if self.notification.status in PlanSubscriptionStatus.DATA_CANCELLED_LIST:
            self.plan_subscription_cancel()

        return Response()
