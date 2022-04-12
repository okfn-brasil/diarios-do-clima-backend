from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsersView,
    UsersMeView,
)

urlpatterns = [
    path('users/', UsersView.as_view(), name='users'),
    path('users/me/', UsersMeView.as_view(), name='users_me'),
]
