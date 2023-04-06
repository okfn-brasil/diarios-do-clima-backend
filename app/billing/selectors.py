from accounts.models import User
from .models import CreditCard


def user_get_current_credit_card(user: User) -> CreditCard:
    return CreditCard.objects.filter(user=user).latest('created_at')
