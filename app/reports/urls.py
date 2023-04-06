from django.urls import path
from .views import (
    ReportsApiView,
    ReportsPublicApiView,
    ReportsPrivateApiView,
    QuotationCreateApiView,
)

urlpatterns = [
    path('public/', ReportsPublicApiView.as_view(), name='reports_public'),
    path('private/', ReportsPrivateApiView.as_view(), name='reports_private'),
    path('quotation/', QuotationCreateApiView.as_view(), name='quotation'),
    path('<uuid:pk>/', ReportsApiView.as_view(), name='reports'),
]
