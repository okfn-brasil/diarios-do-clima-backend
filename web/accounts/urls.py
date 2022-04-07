from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserModelViewSet,
    UsersMeViewSet
)

users_me_router = DefaultRouter()
users_me_router.register(r'', UsersMeViewSet)

urlpatterns = [
    path('/users', UserCreateView.as_view(), name='users_create'),
    path('/users/me', include(users_me_router.urls)),
]
