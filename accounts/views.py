from django.conf import settings
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import (
    UserOutputSerializer,
    UserInputSerializer,
    UserCreateInputSerializer,
)


class MultiSerializerModelView(object):
    serializers = {}

    def get_serializer_class(self):
        action = self.request.method.lower()
        return self.serializers.get(action, self.serializer_class)


class UsersMeView(
    MultiSerializerModelView,
    UpdateAPIView,
    RetrieveUpdateAPIView
):
    queryset = User.objects.all()
    serializer_class = UserOutputSerializer
    permission_classes = [IsAuthenticated]
    serializers = {
        'retrieve': UserOutputSerializer,
        'update': UserInputSerializer,
        'partial_update': UserInputSerializer,
    }

    def get_object(self):
        return self.request.user


class UsersView(CreateAPIView):
    authentication_classes = []
    serializer_class = UserCreateInputSerializer
