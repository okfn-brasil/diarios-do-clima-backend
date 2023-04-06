import xml.etree.ElementTree as ET
import requests
from .pag_seguro_api_abc import PagSeguroApiABC, PreApprovalNotification
from .serializers import SubscribeSerializer, CreditCardChangeData
from .exceptions import PreApprovalsValidationException, GenericSessionError

from requests.adapters import HTTPAdapter, Retry


class PagSeguroApi(PagSeguroApiABC):
    headers = {
        "Accept": "application/vnd.pagseguro.com.br.v3+json;charset=ISO-8859-1",
        "Content-Type": "application/json; charset=UTF-8"
    }

    def __init__(self, email: str, token: str, ws_url: str) -> None:
        self.email = email
        self.token = token
        self.ws_url = ws_url
        self.auth = f"email={self.email}&token={self.token}"

    def get_session(self) -> str:
        request_session = requests.Session()
        retries = Retry(total=5, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        request_session.mount('http://', HTTPAdapter(max_retries=retries))
        request_session.mount('https://', HTTPAdapter(max_retries=retries))

        url = f"{self.ws_url}/v2/sessions?{self.auth}"
        response = request_session.post(url)

        if response.status_code != 200:
            raise GenericSessionError("erro generating session")

        session = ET.fromstring(response.text)
        id = session.find('id')
        return id.text

    def subscription_create(self, serializer: SubscribeSerializer) -> str:
        url = f"{self.ws_url}/pre-approvals?{self.auth}"

        response = requests.post(
            url,
            json=serializer.json(),
            headers=self.headers
        )

        if response.status_code != 200:
            raise PreApprovalsValidationException(response.json())

        data = response.json()
        code = data['code']
        return code

    def subscription_cancel(self, subscription_code: str) -> None:
        url = f"{self.ws_url}/pre-approvals/{subscription_code}/cancel?{self.auth}"

        response = requests.put(url, headers=self.headers)

        if response.status_code != 204:
            raise Exception("something went wrong")

    def subscription_get_notification(self, notification_code: str) -> PreApprovalNotification:
        url = f"{self.ws_url}/pre-approvals/notifications/{notification_code}?{self.auth}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(response.json())

        data = response.json()
        return PreApprovalNotification(
            code=data['code'],
            date=data['date'],
            status=data['status'],
        )

    def subscription_change_credit_card(self, subscription_code: str, data: CreditCardChangeData) -> None:
        url = f"{self.ws_url}/pre-approvals/{subscription_code}/payment-method?{self.auth}"

        response = requests.put(url, json=data.json(), headers=self.headers)

        if response.status_code != 204:
            raise Exception(response.json())

    def subscription_orders(self, subscription_code: str):
        url = f"{self.ws_url}/pre-approvals/{subscription_code}/payment-orders?{self.auth}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(response.json())

        data = response.json()
        from .serializers.models import OrdersResult, Order
        result = OrdersResult(**data)
        orders = [Order(**result.paymentOrders[orderKey])
                  for orderKey in result.paymentOrders]
        orders.sort(
            reverse=True,
            key=lambda order: order.schedulingDate
        )

        return [order.dict() for order in orders]
