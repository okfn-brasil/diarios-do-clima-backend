from rest_framework import serializers
from .models import (
    Phone,
    Address,
    CreditCard,
)


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = (
            "area_code",
            "number",
        )


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "street",
            "number",
            "complement",
            "district",
            "city",
            "state",
            "country",
            "postal_code"
        )


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = (
            "token",
            "last_four_digits",
            "exp_month",
            "exp_year",
            "holder_name",
            "holder_birth_date",
            "cpf",
        )
