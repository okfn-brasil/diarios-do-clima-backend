from django.urls import path
from .views import (
    PhoneView,
    AddressView,
    CreditCardView,
    PagSeguroSession,
)


urlpatterns = [
    path('phone/', PhoneView.as_view(), name='phone'),
    path('credit_card/', CreditCardView.as_view(), name='credit_card'),
    path('address/', AddressView.as_view(), name='address'),    
    path('session/', PagSeguroSession.as_view(), name='sessions'),
]
