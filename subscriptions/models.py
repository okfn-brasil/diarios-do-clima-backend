from django.db import models
from django.contrib.auth import get_user_model
from plans.models import Plan

User = get_user_model()


class PlanSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
