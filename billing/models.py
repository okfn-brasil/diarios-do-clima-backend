from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from validate_docbr import CPF

User = get_user_model()


def validate_cpf(value: str) -> None:
    cpf = CPF()
    if not cpf.validate(value):
        raise ValidationError(
            _('%(value)s is not an valid CPF'),
            params={'value': value},
        )


class Phone(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    area_code = models.CharField(max_length=2)
    number = models.CharField(max_length=9)


class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=50)
    number = models.CharField(max_length=7)
    complement = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=3)
    postal_code = models.CharField(max_length=8)


class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, unique=True)
    last_four_digits = models.CharField(max_length=4)
    exp_month = models.CharField(max_length=2)
    exp_year = models.CharField(max_length=4)
    holder_name = models.CharField(max_length=50)
    holder_birth_date = models.DateField()
    cpf = models.CharField(max_length=11, validators=[validate_cpf])
    created_at = models.DateTimeField(auto_now_add=True)
