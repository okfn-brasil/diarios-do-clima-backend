import uuid
from django.db import models


class Plan(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    html = models.TextField()
    pagseguro_plan_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    trial_days = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def to_charge(self) -> bool:
        trial = self.trial_days is not None
        pagseguro = self.pagseguro_plan_id is not None
        return trial and pagseguro
