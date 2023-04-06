from django.urls import path
from .views import (
    PlanApiView,
)

urlpatterns = [
    path('', PlanApiView.as_view(), name='plans'),
]
