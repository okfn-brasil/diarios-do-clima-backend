import uuid
from django.db import models


class Plan(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    card = models.TextField()
    price = models.DecimalField()
    pagseguro_plan_id = models.CharField(unique=True)
