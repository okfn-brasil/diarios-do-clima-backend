from django.urls import path
from .views import (
    PhoneView,
    AddressView,
    CreditCardView,
    PagSeguroSessionView,
)


urlpatterns = [
    path('phone/', PhoneView.as_view(), name='phone'),
    path('credit_card/', CreditCardView.as_view(), name='credit_card'),
    path('address/', AddressView.as_view(), name='address'),
    path('session/', PagSeguroSessionView.as_view(), name='session'),
]
