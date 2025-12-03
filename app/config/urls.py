from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("plans/", include("plans.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("billing/", include("billing.urls")),
    path("reports/", include("reports.urls")),
    path("alerts/", include("alerts.urls")),
    path("querido_diario/", include("querido_diario.urls")),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("health/", include("health_check.urls")),
]
