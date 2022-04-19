from django.db import models
from django.contrib.auth import get_user_model
from plans.models import Plan

User = get_user_model()


class PlanSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.plan}'


class PlanSubscriptionStatus(models.Model):
    DATA_ACTIVE = 'ACTIVE'
    DATA_PAYMENT_METHOD_CHANGE = 'PAYMENT_METHOD_CHANGE'

    DATA_CHOICES = (
        (DATA_ACTIVE, DATA_ACTIVE),
        (DATA_PAYMENT_METHOD_CHANGE, DATA_PAYMENT_METHOD_CHANGE)
    )

    plan_subscription = models.ForeignKey(
        PlanSubscription, on_delete=models.CASCADE)
    pagseguro_data = models.CharField(max_length=25, choices=DATA_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def data(self):
        return self.DATA_ACTIVE

    class Meta:
        verbose_name = "Plan Subscription Status"
        verbose_name_plural = "Plan Subscription Statuses"

    def __str__(self) -> str:
        return self.data
