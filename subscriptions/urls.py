from django.urls import path
from .views import (
    NotificationsApiView,
    PlanSubscriptionApiView,
)

urlpatterns = [
    path('', PlanSubscriptionApiView.as_view(), name='subscriptions'),
    path('notifications/', NotificationsApiView.as_view(), name='notifications'),
]
