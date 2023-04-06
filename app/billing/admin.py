from django.contrib import admin
from .models import (
    Phone,
    Address,
    CreditCard,
)


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    pass
