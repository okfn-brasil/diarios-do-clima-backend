from libs.utils.email import Email, send_email
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

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


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    uri = reverse('password_reset:reset-password-confirm')
    key = reset_password_token.key
    reset_password_url = "{}?token={}".format(
        instance.request.build_absolute_uri(uri), key,
    )

    send_email(Email(
        subject="Password Reset for {title}".format(title="Diario do Clima"),
        email_to=[reset_password_token.user.email],
        message=reset_password_url,
    ))

