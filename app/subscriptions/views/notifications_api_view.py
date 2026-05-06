from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import PlanSubscription, PlanSubscriptionStatus
from ..actions import user_plan_subscription_cancel
from ..selectors import user_get_latest_plan_subscription
from libs.pagseguro import PreApprovalNotification
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NotificationsApiView(APIView):
    notification_type = 'preApproval'

    def plan_subscription_status_update(self, notification_code: str, subscription_code: str, date_str: str, status: str):
        self.notification = PreApprovalNotification(
            code=subscription_code,
            date=date_str,
            status=status
        )

        try:
            self.plan_subscription = PlanSubscription.objects.get(pagseguro_code=subscription_code)
        except PlanSubscription.DoesNotExist:
            logger.warning(f"PlanSubscription with code {subscription_code} not found")
            return

        try:
            # Try parsing with and without milliseconds
            if '.' in date_str:
                date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
            else:
                date_format = '%Y-%m-%dT%H:%M:%S%z'
            pagseguro_notification_date = timezone.datetime.strptime(date_str, date_format)
        except (ValueError, TypeError):
            pagseguro_notification_date = timezone.now()

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
        # Support for V3 Webhooks (JSON payload)
        data = request.data
        if 'event' in data and data['event'].startswith('subscription.'):
            resource = data.get('resource', {})
            subscription_code = resource.get('id')
            status_raw = resource.get('status')
            date_str = resource.get('updated_at', resource.get('created_at', ''))
            
            # Using the event id or generate a unique one if not provided directly
            notification_code = data.get('id', f"webhook_{subscription_code}_{date_str}")
            
            # Map V3 status to V2 internal statuses
            status = status_raw
            if status_raw == 'CANCELED':
                status = PlanSubscriptionStatus.DATA_CANCELLED
            elif status_raw in ['OVERDUE', 'PAST_DUE']:
                status = PlanSubscriptionStatus.DATA_PENDING
                
            self.plan_subscription_status_update(
                notification_code=notification_code,
                subscription_code=subscription_code,
                date_str=date_str,
                status=status
            )
            
            if hasattr(self, 'plan_subscription') and self.notification.status in PlanSubscriptionStatus.DATA_CANCELLED_LIST:
                self.plan_subscription_cancel()
                
            return Response()

        # Support for Legacy V2 Webhooks
        notification_code = request.POST.get('notificationCode')
        notification_type = request.POST.get('notificationType')

        if notification_type != self.notification_type:
            return Response()
            
        from libs.services import services
        from libs.pagseguro import PagSeguroApiABC
        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        
        legacy_notification = pag_seguro_api.subscription_get_notification(notification_code)
        self.plan_subscription_status_update(
            notification_code=notification_code,
            subscription_code=legacy_notification.code,
            date_str=legacy_notification.date,
            status=legacy_notification.status
        )

        if hasattr(self, 'plan_subscription') and self.notification.status in PlanSubscriptionStatus.DATA_CANCELLED_LIST:
            self.plan_subscription_cancel()

        return Response()
