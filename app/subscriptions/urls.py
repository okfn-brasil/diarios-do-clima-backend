from django.urls import path
from .views import (
    NotificationsApiView,
    PlanSubscriptionApiView,
    PlanSubscriptionCancelAPIView,
    PlanSubscriptionOrdersApiView,
)

urlpatterns = [
    path('', PlanSubscriptionApiView.as_view(), name='subscriptions'),
    path('cancel/', PlanSubscriptionCancelAPIView.as_view(), name='subscriptions_cancel'),
    path('orders/<int:pk>/', PlanSubscriptionOrdersApiView.as_view(), name='orders'),
    path('notifications/', NotificationsApiView.as_view(), name='notifications'),
]
