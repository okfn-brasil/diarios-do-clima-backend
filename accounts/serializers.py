from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .selectors import user_get_current_plan_subscription
from plans.models import Plan
from subscriptions.models import PlanSubscription, PlanSubscriptionStatus
from subscriptions.selectors import plan_subscription_get_latest_status
from billing.serializers import CreditCardSerializer, AddressSerializer, PhoneSerializer
from billing.selectors import user_get_current_credit_card
from billing.models import CreditCard


class UserInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "alert_email",
            "full_name",
            "city",
            "state",
            "gender",
            "sector",
        ]


class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "title",
            "pagseguro_plan_id",
        )


class UserPlanSubscriptionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanSubscriptionStatus
        fields = (
            "id",
            "data",
            "created_at",
        )


class UserPlanSubscriptionSerializer(serializers.ModelSerializer):
    plan = UserPlanSerializer()
    status = serializers.SerializerMethodField()

    class Meta:
        model = PlanSubscription
        fields = (
            "id",
            "plan",
            "status",
            "created_at",
        )

    def get_status(self, plan_subscription):
        try:
            plan_subscription_status = plan_subscription_get_latest_status(
                plan_subscription=plan_subscription)
            plan_subscription_status_serializer = UserPlanSubscriptionStatusSerializer(
                plan_subscription_status)
            return plan_subscription_status_serializer.data
        except PlanSubscriptionStatus.DoesNotExist:
            return None


class UserPlanSubscriptionSerializerMixin(metaclass=serializers.SerializerMetaclass):
    plan_subscription = serializers.SerializerMethodField()

    def get_plan_subscription(self, user):
        try:
            plan_subscription = user_get_current_plan_subscription(user=user)
        except PlanSubscription.DoesNotExist:
            return None

        plan_subscription_serializer = UserPlanSubscriptionSerializer(
            plan_subscription,
        )
        return plan_subscription_serializer.data


class UserCreateInputSerializer(serializers.ModelSerializer, UserPlanSubscriptionSerializerMixin):
    jwt = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "alert_email",
            "password",
            "full_name",
            "city",
            "state",
            "gender",
            "sector",
            "plan_subscription",
            "jwt",
        ]

        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
        }

    def validate_password(self, value: str) -> str:
        return make_password(value)

    def get_jwt(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserOutputSerializer(UserPlanSubscriptionSerializerMixin, serializers.ModelSerializer):

    credit_card = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)
    phone = PhoneSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "alert_email",
            "full_name",
            "city",
            "state",
            "gender",
            "sector",
            "address",
            "phone",
            "credit_card",
            "plan_subscription",
            "last_login",
            "date_joined",
        ]

    def get_credit_card(self, user):
        try:
            credit_card = user_get_current_credit_card(user=user)
        except CreditCard.DoesNotExist:
            return None

        credit_card_serializer = CreditCardSerializer(
            credit_card,
        )
        return credit_card_serializer.data
