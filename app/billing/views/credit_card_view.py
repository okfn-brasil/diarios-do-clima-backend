from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from subscriptions.selectors import user_get_latest_plan_subscription
from plans.models import Plan
from subscriptions.models import PlanSubscription
from ..serializers import (
    CreditCardSerializer,
)

from ..models import (
    Address,
    CreditCard,
    Phone,
)

from libs.pagseguro import PagSeguroApiABC
from libs.pagseguro.serializers import (
    BillingAddressData,
    BillingDocumentData,
    BillingPhoneData,
    CreditCardHolderData,
    CreditCardChangeData,
)
from libs.services import services
from libs.get_client_ip import get_client_ip
from libs.utils.datetime import datetime_to_date_str
from django.db import transaction


from accounts.models import User


def get_billing_phone(user: User) -> BillingPhoneData:
    phone: Phone = user.phone
    return BillingPhoneData(
        area_code=phone.area_code,
        number=phone.number,
    )


def get_billing_address(user: User) -> BillingAddressData:
    address: Address = user.address
    return BillingAddressData(
        street=address.street,
        number=address.number,
        complement=address.complement,
        district=address.district,
        city=address.city,
        state=address.state,
        country=address.country,
        postal_code=address.postal_code,
    )


def get_credit_card_holder(user: User, credit_card: CreditCard) -> CreditCardHolderData:
    return CreditCardHolderData(
        name=credit_card.holder_name,
        biling_phone=get_billing_phone(user=user),
        billing_address=get_billing_address(user=user),
        bith_date=datetime_to_date_str(date=credit_card.holder_birth_date),
        documents=[
            BillingDocumentData(
                type='CPF',
                value=credit_card.cpf,
            ),
        ]
    )


def get_credit_card_change_data(ip: str, user: User, credit_card: CreditCard) -> CreditCardChangeData:
    return CreditCardChangeData(
        ip=ip,
        credit_card_holder=get_credit_card_holder(
            user=user, credit_card=credit_card
        ),
        credit_card_token=credit_card.token,
    )


class CreditCardView(ListAPIView, CreateAPIView):
    serializer_class = CreditCardSerializer
    queryset = CreditCard.objects.all()
    permission_classes = [IsAuthenticated]

    def pagseguro_validation(self):
        try:
            self.request.user.phone
        except Phone.DoesNotExist:
            raise ValidationError(
                {"phone": ["user phone does not exist"]},
            )

        try:
            self.request.user.address
        except Address.DoesNotExist:
            raise ValidationError(
                {"address": ["user address does not exist"]},
            )

    def pagseguro_change_credit_card(
        self,        
        credit_card: CreditCard,
        plan_subscription: PlanSubscription,
    ):
        self.pagseguro_validation()        
        pag_seguro_api: PagSeguroApiABC = services.get(PagSeguroApiABC)
        ip = get_client_ip(self.request)
        change_data = get_credit_card_change_data(
            ip=ip,
            user=self.request.user,
            credit_card=credit_card,
        )

        pag_seguro_api.subscription_change_credit_card(
            subscription_code=plan_subscription.pagseguro_code,
            data=change_data
        )

    def perform_create(self, serializer):
        with transaction.atomic():            
            credit_card: CreditCard = serializer.save(user=self.request.user)
            current_plan_subscription = user_get_latest_plan_subscription(
                user=self.request.user,
            )
            plan: Plan = current_plan_subscription.plan
            if plan.to_charge():
                self.pagseguro_change_credit_card(                    
                    credit_card=credit_card,
                    plan_subscription=current_plan_subscription,
                )
