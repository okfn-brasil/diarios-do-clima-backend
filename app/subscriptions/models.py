from django.db import models
from django.contrib.auth import get_user_model
from plans.models import Plan

User = get_user_model()


class PlanSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    pagseguro_code = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    trial_end_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.plan}'


class PlanSubscriptionStatus(models.Model):

    DATA_INITIATED = 'INITIATED'
    DATA_PENDING = 'PENDING'
    DATA_ACTIVE = 'ACTIVE'
    DATA_PAYMENT_METHOD_CHANGE = 'PAYMENT_METHOD_CHANGE'
    DATA_SUSPENDED = 'SUSPENDED'
    DATA_CANCELLED = 'CANCELLED'
    DATA_CANCELLED_BY_RECEIVER = 'CANCELLED_BY_RECEIVER'
    DATA_CANCELLED_BY_SENDER = 'CANCELLED_BY_SENDER'
    DATA_EXPIRED = 'EXPIRED'
    DATA_UNKNOWN = 'UNKNOWN'

    DATA_CHOICES = (
        (DATA_INITIATED, DATA_INITIATED),
        (DATA_PENDING, DATA_PENDING),
        (DATA_ACTIVE, DATA_ACTIVE),
        (DATA_PAYMENT_METHOD_CHANGE, DATA_PAYMENT_METHOD_CHANGE),
        (DATA_SUSPENDED, DATA_SUSPENDED),
        (DATA_CANCELLED, DATA_CANCELLED),
        (DATA_CANCELLED_BY_RECEIVER, DATA_CANCELLED_BY_RECEIVER),
        (DATA_CANCELLED_BY_SENDER, DATA_CANCELLED_BY_SENDER),
        (DATA_EXPIRED, DATA_EXPIRED),
    )

    DATA_CANCELLED_LIST = [
        DATA_CANCELLED,
        DATA_CANCELLED_BY_RECEIVER,
        DATA_CANCELLED_BY_SENDER,
        DATA_EXPIRED
    ]

    DATA_PENDING_LIST = [
        DATA_INITIATED,
        DATA_PENDING,
        DATA_PAYMENT_METHOD_CHANGE,
        DATA_SUSPENDED,
    ]

    plan_subscription = models.ForeignKey(
        PlanSubscription, on_delete=models.CASCADE,
    )

    pagseguro_data = models.CharField(max_length=25, choices=DATA_CHOICES)
    pagseguro_notification_code = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        unique=True,
    )
    pagseguro_notification_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def data(self):
        if self.pagseguro_data == self.DATA_ACTIVE:
            return self.DATA_ACTIVE

        elif self.pagseguro_data in self.DATA_PENDING_LIST:
            return self.DATA_PENDING

        elif self.pagseguro_data in self.DATA_CANCELLED_LIST:
            return self.DATA_CANCELLED

        return self.DATA_UNKNOWN

    class Meta:
        verbose_name = "Plan Subscription Status"
        verbose_name_plural = "Plan Subscription Statuses"

    def __str__(self) -> str:
        return self.data
