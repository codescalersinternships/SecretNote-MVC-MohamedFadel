import uuid

from django.db import models
from django.utils import timezone


class SecretNote(models.Model):
    content = models.TextField()
    url_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    max_views = models.IntegerField(default=1)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        if self.expiration_time and timezone.now() > self.expiration_time:
            return True

        if self.views > self.max_views:
            return True

        return False

    def increment_view(self):
        self.views += 1
        self.save()

    def __str__(self):
        return f"SecretNote {self.url_key}"
