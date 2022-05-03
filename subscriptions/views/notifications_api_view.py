from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import PlanSubscription, PlanSubscriptionStatus
from ..actions import user_plan_subscription_cancel
from libs.services import services
from libs.pagseguro import PagSeguroApiABC, PreApprovalNotification
from django.utils import timezone


class NotificationsApiView(APIView):
    notification_type = 'preApproval'

    def post(self, request, *args, **kwargs):
        notification_code = request.POST.get('notificationCode')
        notification_type = request.POST.get('notificationType')

        if notification_type != self.notification_type:
            return Response()

        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        notification: PreApprovalNotification = pag_seguro_api.subscription_get_notification(
            notification_code=notification_code)

        plan_subscription = PlanSubscription.objects.get(
            pagseguro_code=notification.code,
        )
        pagseguro_notification_date = timezone.datetime.strptime(
            notification.date,
            '%Y-%m-%dT%H:%M:%S%z',
        )

        try:
            PlanSubscriptionStatus.objects.get(
                pagseguro_notification_code=notification_code)
        except PlanSubscriptionStatus.DoesNotExist:
            plan_subscription_status = PlanSubscriptionStatus(
                plan_subscription=plan_subscription,
                pagseguro_data=notification.status,
                pagseguro_notification_code=notification_code,
                pagseguro_notification_date=pagseguro_notification_date
            )
            plan_subscription_status.save()

        if notification.status in PlanSubscriptionStatus.DATA_CANCELLED_LIST:
            user_plan_subscription_cancel(
                user=plan_subscription.user,
            )

        return Response()
