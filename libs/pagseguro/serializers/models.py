from datetime import datetime
from pydantic import BaseModel


class OrdersResult(BaseModel):
    date: datetime
    resultsInThisPage: str
    totalPages: int
    currentPage: int
    paymentOrders: dict


class Order(BaseModel):
    code: str
    status: int
    amount: float
    lastEventDate: datetime
    schedulingDate: datetime

    def get_status_verbose(self) -> str:
        if self.status == 1:
            return "agendado"
        elif self.status == 5:
            return "pago"
        return ""

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['status_verbose'] = self.get_status_verbose()
        return data
