from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsersMeViewSet
)

users_me_router = DefaultRouter()
users_me_router.register(r'users/me', UsersMeViewSet)

urlpatterns = [
    *users_me_router.urls
]
