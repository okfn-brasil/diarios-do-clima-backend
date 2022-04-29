class SubscribeSerializer:

    def __init__(self, user, plan_subscription, ip: str) -> None:
        self.user = user
        self.plan_subscription = plan_subscription
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

    def get_sender(self, user, ip: str) -> dict:
        return {
            "name": user.creditcard.holder_name,
            "email": user.email,
            "ip": ip,
            "phone": self.get_sender_phone(user=user),
            "address": self.get_sender_address(user=user),
            "documents": [
                {
                    "type": "CPF",
                    "value": user.creditcard.cpf
                }
            ]
        }

    def get_payment_method(self, user, ) -> dict:
        return {
            "type": "CREDITCARD",
            "creditCard": {
                "token": user.creditcard.token,
                "holder": {
                    "name": user.creditcard.holder_name,
                    "birthDate": str(user.creditcard.holder_birth_date.strftime("%d/%m/%Y")),
                    "documents": [
                        {
                            "type": "CPF",
                            "value": user.creditcard.cpf
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
            "sender": self.get_sender(user=self.user, ip=self.ip),
            "paymentMethod": self.get_payment_method(user=self.user)
        }
        return data
