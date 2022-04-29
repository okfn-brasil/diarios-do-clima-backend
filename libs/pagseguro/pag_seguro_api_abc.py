import abc
from .serializers import SubscribeSerializer


class PagSeguroApiABC(abc.ABC):

    @abc.abstractmethod
    def get_session(self) -> str:
        """get a pagseguro session id"""

    @abc.abstractmethod
    def subscribe(self, serializer: SubscribeSerializer) -> str:
        """create plan subscription"""
