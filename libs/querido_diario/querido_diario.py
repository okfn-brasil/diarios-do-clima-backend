from typing import List
import requests
from .querido_diario_abc import QueridoDiarioABC
from .serializers import GazetteFilters, GazettesResult
from rest_framework.exceptions import NotFound


class QueridoDiario(QueridoDiarioABC):

    def __init__(self, api_url: str) -> None:
        self.api_url: str = api_url

    def cnpj_info(self, cnpj: str) -> dict:
        """get querido diario cnpj info"""

        url = f"{self.api_url}/api/company/info/{cnpj}"
        response = requests.get(url)
        if response.status_code != 200:
            raise NotFound("CNPJ não encontrado!")

        data = response.json()
        return data

    def cnpj_list_partners(self, cnpj: str) -> dict:
        """get cnpj partners list"""
        url = f"{self.api_url}/api/company/partners/{cnpj}"
        response = requests.get(url)
        if response.status_code != 200:
            raise NotFound("CNPJ não encontrado!")

        data = response.json()
        return data

    def gazettes(self, filters: GazetteFilters) -> GazettesResult:
        """get cnpj partners list"""

        url = f"{self.api_url}/api/gazettes/by_theme/Políticas%20Ambientais%20Nacionais"
        response = requests.get(url, params=filters.json())

        if response.status_code == 404:
            raise NotFound("CNPJ não encontrado!")

        data: dict = response.json()
        return GazettesResult.from_json(data)
