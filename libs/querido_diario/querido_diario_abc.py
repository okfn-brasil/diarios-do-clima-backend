from typing import List
import abc
from .serializers import GazettesResult, GazetteFilters


class QueridoDiarioABC(abc.ABC):

    @abc.abstractmethod
    def cnpj_info(self, cnpj: str) -> dict:
        """get querido diario cnpj info"""

    @abc.abstractmethod
    def cnpj_list_partners(self, cnpj: str) -> List[dict]:
        """get cnpj partners list"""

    @abc.abstractmethod
    def gazettes(self, filters: GazetteFilters) -> GazettesResult:
        """get cnpj partners list"""
