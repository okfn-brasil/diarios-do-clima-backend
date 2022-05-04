from django.urls import path
from .views import (
    ReportsApiView,
    ReportsPublicApiView,
    ReportsPrivateApiView,
)

urlpatterns = [
    path('public/', ReportsPublicApiView.as_view(), name='reports_public'),
    path('private/', ReportsPrivateApiView.as_view(), name='reports_private'),
    path('<uuid:pk>/', ReportsApiView.as_view(), name='reports'),
]
