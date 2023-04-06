from django.db import transaction
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import APIException
from ..serializers import QuotationSerializer
from reports.models import Quotation
from libs.utils.email import Email, send_email
from django.conf import settings


class QuotationCreateApiView(CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = QuotationSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            quotation: Quotation = serializer.save()
            message = f"{quotation.id}\n"
            message += f"{quotation.name}\n"
            message += f"{quotation.email}\n"
            message += f"{quotation.message}\n"
            
            try:
                subject = f"Cotação de relatório de {quotation.name}"
                send_email(email=Email(
                    subject=subject,
                    email_to=[settings.QUOTATION_TO_EMAIL],
                    message=message,
                ))
            except:
                raise APIException('Erro ao mandar email')
            return quotation
