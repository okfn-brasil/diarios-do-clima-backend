from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Phone(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    area_code = models.CharField(max_length=2)
    number = models.CharField(max_length=9)


class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=50)
    number = models.CharField(max_length=3)
    complement = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=3)
    postal_code = models.CharField(max_length=8)


class CreditCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50)
    last_four_digits = models.CharField(max_length=4)
    exp_month = models.CharField(max_length=2)
    exp_year = models.CharField(max_length=4)
    holder_name = models.CharField(max_length=50)
    holder_birth_date = models.DateField()  # TODO: verificar se é obrigatorio
    cpf = models.CharField(max_length=11)  # TODO: validação de cpf
