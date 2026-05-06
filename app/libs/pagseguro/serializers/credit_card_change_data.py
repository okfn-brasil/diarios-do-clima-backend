from dataclasses import dataclass
import abc
from typing import List


class JSONSerializeble(abc.ABC):

    @abc.abstractmethod
    def json(self) -> dict:
        """return dict representing json"""


@dataclass
class BillingDocumentData(JSONSerializeble):
    type: str # 'CPF' or 'CNPJ' usually
    value: str

    def json(self):
        return {
            "type": self.type,
            "value": self.value,
        }


@dataclass
class CreditCardHolderData(JSONSerializeble):
    name: str

    def json(self):
        return {
            "name": self.name
        }


@dataclass
class CreditCardChangeData(JSONSerializeble):
    ip: str
    credit_card_token: str
    credit_card_holder: CreditCardHolderData

    def json(self):
        return {
            "payment_method": {
                "type": "CREDIT_CARD",
                "credit_card": {
                    "token": self.credit_card_token,
                    "holder": self.credit_card_holder.json()
                }
            }
        }
