from rest_framework.routers import DefaultRouter
from .views import UserModelViewSet

accounts_router = DefaultRouter()
accounts_router.register(r'users', UserModelViewSet, basename='users')

urlpatterns = accounts_router.urls
