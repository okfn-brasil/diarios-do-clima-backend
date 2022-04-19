from django.urls import path
from .views import (
    PlanSubscriptionApiView,
)

urlpatterns = [
    path('', PlanSubscriptionApiView.as_view(), name='subscriptions'),
]
