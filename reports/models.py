import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Report(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    public = models.BooleanField(default=False)


class ReportUserAccess(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            'report',
            'user',
        )
