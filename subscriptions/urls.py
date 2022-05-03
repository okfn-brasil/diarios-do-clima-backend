from django.urls import path
from .views import (
    NotificationsApiView,
    PlanSubscriptionApiView,
    PlanSubscriptionCancelAPIView,
)

urlpatterns = [
    path('', PlanSubscriptionApiView.as_view(), name='subscriptions'),
    path('cancel/', PlanSubscriptionCancelAPIView.as_view(), name='subscriptions_cancel'),
    path('notifications/', NotificationsApiView.as_view(), name='notifications'),
]
