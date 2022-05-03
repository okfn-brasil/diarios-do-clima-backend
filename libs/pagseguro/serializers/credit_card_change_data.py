from dataclasses import dataclass
import abc
from typing import List


class JSONSerializeble(abc.ABC):

    @abc.abstractmethod
    def json(self) -> dict:
        """return dict representing json"""


@dataclass
class BillingAddressData(JSONSerializeble):
    street: str
    number: str
    complement: str
    district: str
    city: str
    state: str
    country: str
    postal_code: str

    def json(self):
        return {
            "street": self.street,
            "number": self.number,
            "complement": self.complement,
            "district": self.district,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postalCode": self.postal_code,
        }


@dataclass
class BillingDocumentData(JSONSerializeble):
    type: str
    value: str

    def json(self):
        return {
            "type": self.type,
            "value": self.value,
        }


@dataclass
class BillingPhoneData(JSONSerializeble):
    area_code: str
    number: str

    def json(self):
        return {
            "areaCode": self.area_code,
            "number": self.number,
        }


@dataclass
class CreditCardHolderData(JSONSerializeble):
    name: str
    bith_date: str
    documents: List[BillingDocumentData]
    biling_phone: BillingPhoneData
    billing_address: BillingAddressData

    def json(self):
        return {
            "name": self.name,
            "birthDate": self.bith_date,
            "documents": [doc.json() for doc in self.documents],
            "phone": self.biling_phone.json(),
            "billingAddress": self.billing_address.json(),
        }


@dataclass
class CreditCardChangeData(JSONSerializeble):
    ip: str
    credit_card_token: str
    credit_card_holder: CreditCardHolderData

    def json(self):
        return {
            "type": "CREDITCARD",
            "sender": {
                "ip": self.ip,
            },
            "creditCard": {
                "token": self.credit_card_token,
                "holder": self.credit_card_holder.json()
            }
        }
