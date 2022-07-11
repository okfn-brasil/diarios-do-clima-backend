from django.urls import path
from .views import (
    UsersView,
    UsersMeView,
    UsersEmailVerify,
)

urlpatterns = [
    path('users/', UsersView.as_view(), name='users'),
    path('users/me/', UsersMeView.as_view(), name='users_me'),
    path(
        'users/email/<str:email>/',
        UsersEmailVerify.as_view(),
        name='users_email_verify',
    )
]
