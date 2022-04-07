from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateAPIView
from .models import User
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserWriteSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'full_name',
            'city',
            'state',
            'gender',
            'sector',
            'password',
        ]


UserRetrieveSerializer = UserWriteSerializer
UserUpdateSerializer = UserWriteSerializer


class MultiSerializerModelViewSet(object):
    serializers = {}

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)


class UsersMeViewSet(
    MultiSerializerModelViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    serializers = {
        'retrieve': UserRetrieveSerializer,
        'update': UserUpdateSerializer,
        'partial_update': UserUpdateSerializer,
    }
