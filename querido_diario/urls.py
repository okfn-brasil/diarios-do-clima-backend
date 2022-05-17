from django.urls import path
from .views import (
    CNPJSView,
    CNPJPartnersView,
    GazettesView
)


urlpatterns = [
    path('cnpjs/<str:cnpj>/', CNPJSView.as_view(), name='cnpjs'),
    path('cnpjs/<str:cnpj>/partners',
         CNPJPartnersView.as_view(), name='cnpjs_partners'),
    path('gazettes/', GazettesView.as_view(), name='gazettes'),
]
