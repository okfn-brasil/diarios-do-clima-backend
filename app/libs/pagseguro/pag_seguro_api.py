import requests
from .pag_seguro_api_abc import PagSeguroApiABC, PreApprovalNotification
from .serializers import SubscribeSerializer, CreditCardChangeData
from .exceptions import PreApprovalsValidationException, GenericSessionError


class PagSeguroApi(PagSeguroApiABC):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def __init__(self, token: str, ws_url: str) -> None:
        self.token = token
        self.ws_url = ws_url

    def _get_auth_headers(self):
        return {
            **self.headers,
            "Authorization": f"Bearer {self.token}"
        }

    def get_session(self) -> str:
        # Em V3, a tokenizacao usa Public Key inves de Session. 
        # Retornaremos a public key para que a mesma view_session anterior passe a devolver a public key pro frontend.
        url = f"{self.ws_url}/public-keys"
        response = requests.post(
            url, 
            headers=self._get_auth_headers(), 
            json={"type": "card"}
        )

        if response.status_code not in [200, 201]:
            raise GenericSessionError(f"Erro ao gerar public key: {response.text}")

        return response.json()['public_key']

    def subscription_create(self, serializer: SubscribeSerializer) -> str:
        url = f"{self.ws_url}/subscriptions"
        
        response = requests.post(
            url,
            json=serializer.json(),
            headers=self._get_auth_headers()
        )

        if response.status_code not in [200, 201]:
            raise PreApprovalsValidationException(response.json())

        data = response.json()
        return data['id']

    def subscription_cancel(self, subscription_code: str) -> None:
        url = f"{self.ws_url}/subscriptions/{subscription_code}/cancel"

        response = requests.put(url, headers=self._get_auth_headers())

        if response.status_code not in [200, 204]:
            raise Exception("something went wrong canceling subscription")

    def subscription_get_notification(self, notification_code: str) -> PreApprovalNotification:
        # A API V3 pode devolver toda a consulta da assinatura atravsedes de GET /subscriptions/{id}
        url = f"{self.ws_url}/subscriptions/{notification_code}"
        response = requests.get(url, headers=self._get_auth_headers())

        if response.status_code != 200:
            raise Exception(response.json())

        data = response.json()
        
        # Map V3 status to V2 internal statuses
        v3_status = data['status']
        v2_status = v3_status
        if v3_status == 'CANCELED':
            v2_status = 'CANCELLED'
            
        return PreApprovalNotification(
            code=data['id'],
            date=data.get('created_at', ''),
            status=v2_status,
        )

    def subscription_change_credit_card(self, subscription_code: str, data: CreditCardChangeData) -> None:
        url_sub = f"{self.ws_url}/subscriptions/{subscription_code}"
        response_sub = requests.get(url_sub, headers=self._get_auth_headers())
        if response_sub.status_code != 200:
            raise Exception(f"Failed to fetch subscription for changing card: {response_sub.text}")
        
        customer_id = response_sub.json().get('customer', {}).get('id')
        if not customer_id:
            raise Exception("Subscription does not have an associated customer_id in V3")

        url = f"{self.ws_url}/customers/{customer_id}/billing_info"
        
        # O JSON devolvido por data.json() contem a estrutura esperada para este endpoint.
        # Que eh {"payment_method": {"type": "CREDIT_CARD", "credit_card": {...}}}
        # Muitas vezes api.pagseguro.com eh requerido para clientes em vez do ws_url (sandbox/etc), 
        # mas manteremos ws_url/customers
        response = requests.put(url, json=data.json(), headers=self._get_auth_headers())

        if response.status_code not in [200, 204]:
            raise Exception(response.json())

    def subscription_orders(self, subscription_code: str):
        url = f"{self.ws_url}/subscriptions/{subscription_code}/invoices"
        response = requests.get(url, headers=self._get_auth_headers())
        if response.status_code != 200:
            raise Exception(response.json())

        data = response.json()
        invoices = data.get('invoices', [])
        
        orders = []
        for invoice in invoices:
            status_map = {
                "CANCELED": 6, # Ajustando status baseados na API V3 vs Models de V2 
                "PAID": 5, 
                "PAYMENT_PENDING": 1,
                "WAITING": 1,
            }
            order_status = status_map.get(invoice.get("status", "WAITING"), 1)
            orders.append({
                "code": invoice.get("id"),
                "status": order_status,
                "amount": float(invoice.get("amount", {}).get("value", 0)) / 100.0,
                "schedulingDate": invoice.get("due_date", invoice.get("created_at")),
                "lastEventDate": invoice.get("created_at")
            })
        
        orders.sort(
            reverse=True,
            key=lambda order: order["schedulingDate"]
        )

        return orders
