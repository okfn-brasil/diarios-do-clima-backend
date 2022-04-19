from django.urls import path
from .views import (
    UsersView,
    UsersMeView,
)

urlpatterns = [
    path('users/', UsersView.as_view(), name='users'),
    path('users/me/', UsersMeView.as_view(), name='users_me'),
]
