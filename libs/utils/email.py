from django.conf import settings
from dataclasses import dataclass
from typing import List
from django.core.mail import send_mail


@dataclass
class Email:
    subject: str
    message: str
    email_to: List[str]


def send_email(email: Email):
    send_mail(
        email.subject,
        email.message,
        settings.EMAIL_HOST_USER,
        email.email_to,
        fail_silently=False,
    )
