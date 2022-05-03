from django.conf import settings
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .models import PlanSubscription, PlanSubscriptionStatus, Plan
from .serializers import PlanSubscriptionSerializer
from .selectors import user_get_latest_plan_subscription
from .actions import user_plan_subscription_cancel
from billing.selectors import user_get_current_credit_card
from libs.services import services
from libs.pagseguro import PagSeguroApiABC, PreApprovalNotification
from libs.pagseguro.serializers import SubscribeSerializer
from django.utils import timezone


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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


class PlanSubscriptionApiView(CreateAPIView):
    serializer_class = PlanSubscriptionSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        with transaction.atomic():
            plan_subscription = serializer.save(user=self.request.user)
            plan_subscription.save()
            plan: Plan = plan_subscription.plan

            if not plan.to_charge():
                plan_subscription_status = PlanSubscriptionStatus(
                    plan_subscription=plan_subscription,
                    pagseguro_data=PlanSubscriptionStatus.DATA_ACTIVE,
                )
                plan_subscription_status.save()
                return

            pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
            subscribe_serializer = SubscribeSerializer(
                user=self.request.user,
                plan_subscription=plan_subscription,
                credit_card=user_get_current_credit_card(
                    user=self.request.user
                ),
                ip=get_client_ip(self.request)
            )
            code = pag_seguro_api.subscription_create(
                serializer=subscribe_serializer)
            plan_subscription.pagseguro_code = code
            plan_subscription.save()


class PlanSubscriptionCancelAPIView(APIView):
    def post(self, request, *args, **kwargs):
        plan_subscription: PlanSubscription = user_get_latest_plan_subscription(
            user=self.request.user,
        )
        plan: Plan = plan_subscription.plan
        if str(plan.id) == settings.DIARIO_DEFAULT_FREE_PLAN_ID:
            raise Exception("can not cancel default free plan")

        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        pag_seguro_api.subscription_cancel(
            subscription_code=plan_subscription.pagseguro_code
        )

        return Response()
