from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from plans.actions import create_user_default_plan_subscription

from libs.utils.email import Email, send_email


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
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    uri = "/redefinir-senha"
    key = reset_password_token.key
    reset_password_url = f"{settings.FRONT_BASE_URL}{uri}?token={key}"

    message = "Olá, \n"
    message += "Você pediu para redefinir sua senha, para fazê-lo basta clicar no link abaixo: \n"
    message += reset_password_url + " \n\n"
    message += "Caso não tenha selecionado essa opção, por favor, ignore este e-mail.\n"

    send_email(
        Email(
            subject=f"[{settings.PROJECT_TITLE}] Redefinição de senha",
            email_to=[reset_password_token.user.email],
            message=message,
        )
    )
