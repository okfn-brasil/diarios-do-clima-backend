import uuid
from dataclasses import dataclass
import requests
from typing import Union

email = ''
token = ''

url = f"https://ws.sandbox.pagseguro.uol.com.br/pre-approvals/request/?email={email}&token={token}"


@dataclass
class Plan(object):
    """ Plan data class"""
    name: str
    details: str
    reference: str
    price: str
    trial: Union[int, None]


def plan_create(plan: Plan):
    trial = f"<trialPeriodDuration>{plan.trial}</trialPeriodDuration>" if plan.trial is not None else ""

    payload = f"""<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
      <preApprovalRequest>
      <reference>{plan.reference}</reference>     
      <preApproval>
        <charge>auto</charge>
        <name>{plan.name}</name>
        <details>{plan.details}</details>
        <amountPerPayment>{plan.price}</amountPerPayment>
        <period>Monthly</period>    
           {trial}
        </preApproval>
      </preApprovalRequest>
    """

    headers = {
        "Accept": "application/vnd.pagseguro.com.br.v3+xml;charset=ISO-8859-1",
        "Content-Type": "application/xml;charset=ISO-8859-1",
    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)


if __name__ == "__main__":
    plan = Plan(
        name='Teste Novo Trial',
        reference=str(uuid.uuid4()),
        details='Teste',
        price='99.00',
        trial=7
    )

    plan_create(plan=plan)
