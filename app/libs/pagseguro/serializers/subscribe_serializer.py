class SubscribeSerializer:

    def __init__(self, user, plan_subscription, credit_card, ip: str) -> None:
        self.user = user
        self.plan_subscription = plan_subscription
        self.credit_card = credit_card
        self.ip = ip

    def get_customer_phone(self, user) -> dict:
        return {
            "country": "55",
            "area": user.phone.area_code,
            "number": user.phone.number,
            "type": "MOBILE"
        }

    def get_plan(self, plan) -> dict:
        return {
            "id": plan.pagseguro_plan_id
        }

    def get_subscription_reference(self, plan_subscription) -> str:
        return str(plan_subscription.pk)

    def get_customer(self, user, credit_card) -> dict:
        tax_id = credit_card.cpf.replace(".", "").replace("-", "") if credit_card.cpf else ""
        return {
            "name": credit_card.holder_name,
            "email": user.email,
            "tax_id": tax_id,
            "phones": [
                self.get_customer_phone(user=user)
            ]
        }

    def get_payment_method(self, credit_card) -> dict:
        return {
            "type": "CREDIT_CARD",
            "credit_card": {
                "token": credit_card.token,
                "holder": {
                    "name": credit_card.holder_name
                }
            }
        }

    def json(self) -> dict:
        data = {
            "reference_id": self.get_subscription_reference(plan_subscription=self.plan_subscription),
            "plan": self.get_plan(plan=self.plan_subscription.plan),
            "customer": self.get_customer(user=self.user, credit_card=self.credit_card),
            "payment_method": self.get_payment_method(credit_card=self.credit_card)
        }
        return data
