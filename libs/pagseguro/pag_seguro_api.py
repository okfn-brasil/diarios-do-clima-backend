import xml.etree.ElementTree as ET
import requests
from .pag_seguro_api_abc import PagSeguroApiABC
from .serializers import SubscribeSerializer


class PagSeguroApi(PagSeguroApiABC):
    def __init__(self, email: str, token: str, ws_url: str) -> None:
        self.email = email
        self.token = token
        self.ws_url = ws_url

    def get_session(self) -> str:
        url = f"{self.ws_url}/v2/sessions?email={self.email}&token={self.token}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data={})
        session = ET.fromstring(response.text)
        id = session.find('id')
        return id.text

    def subscribe(self, serializer: SubscribeSerializer) -> str:
        url = f"{self.ws_url}/pre-approvals?email={self.email}&token={self.token}"

        headers = {
            "Accept": "application/vnd.pagseguro.com.br.v3+json;charset=ISO-8859-1",
            "Content-Type": "application/json; charset=UTF-8"
        }

        response = requests.post(
            url,
            json=serializer.json(),
            headers=headers
        )

        if response.status_code != 200:
            raise Exception()

        data = response.json()
        code = data['code']
        return code
