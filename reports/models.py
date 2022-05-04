import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def file_upload_to(instance, filename):
    name = uuid.uuid4()
    ext = filename.split('.')[-1]
    return f"{instance.pk}/{name}.{ext}"


class Report(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    file = models.FileField(upload_to=file_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)


class ReportUserAccess(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            'report',
            'user',
        )
