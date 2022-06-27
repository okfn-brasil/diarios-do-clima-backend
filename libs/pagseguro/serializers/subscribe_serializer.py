from libs.utils.datetime import datetime_to_date_str
class SubscribeSerializer:

    def __init__(self, user, plan_subscription, credit_card, ip: str) -> None:
        self.user = user
        self.plan_subscription = plan_subscription
        self.credit_card = credit_card
        self.ip = ip

    def get_sender_phone(self, user) -> dict:

        return {
            "areaCode": user.phone.area_code,
            "number": user.phone.number,
        }

    def get_sender_address(self, user) -> dict:
        return {
            "street": user.address.street,
            "number": user.address.number,
            "complement": user.address.complement,
            "district": user.address.district,
            "city": user.address.city,
            "state": user.address.state,
            "country": user.address.country,
            "postalCode": user.address.postal_code,
        }

    def get_plan_code(self, plan) -> str:
        return plan.pagseguro_plan_id

    def get_subscription_reference(self, plan_subscription) -> str:
        return str(plan_subscription.pk)

    def get_sender(self, user, credit_card, ip: str) -> dict:
        return {
            "name": credit_card.holder_name,
            "email": user.email,
            "ip": ip,
            "phone": self.get_sender_phone(user=user),
            "address": self.get_sender_address(user=user),
            "documents": [
                {
                    "type": "CPF",
                    "value": credit_card.cpf
                }
            ]
        }

    def get_payment_method(self, user, credit_card) -> dict:
        return {
            "type": "CREDITCARD",
            "creditCard": {
                "token": credit_card.token,
                "holder": {
                    "name": credit_card.holder_name,
                    "birthDate": datetime_to_date_str(date=credit_card.holder_birth_date),
                    "documents": [
                        {
                            "type": "CPF",
                            "value": credit_card.cpf
                        }
                    ],
                    "phone": self.get_sender_phone(user=user),
                }
            }
        }

    def json(self) -> dict:
        data = {
            "plan": self.get_plan_code(plan=self.plan_subscription.plan),
            "reference": self.get_subscription_reference(plan_subscription=self.plan_subscription),
            "sender": self.get_sender(user=self.user, credit_card=self.credit_card, ip=self.ip),
            "paymentMethod": self.get_payment_method(user=self.user, credit_card=self.credit_card)
        }
        return data
