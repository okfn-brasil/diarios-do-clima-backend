from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from plans.actions import (
    create_user_default_plan_subscription
)


def user_post_save_default_subscription(sender, instance, created, **kwargs):
    if not created:
        return

    create_user_default_plan_subscription(
        user=instance,
    )


def init_signals(app: AppConfig):
    User = get_user_model()
    post_save.connect(user_post_save_default_subscription, sender=User)
