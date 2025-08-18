from django.db import models
from django.conf import settings

class Task(models.Model):
    """
    Represents a background task submitted by a user.
    We store metadata so the orchestration engine can monitor execution.
    """

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (IN_PROGRESS, "In Progress"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    celery_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stores the Celery task UUID"
    )
    result = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional: stores result/response from Celery"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"
