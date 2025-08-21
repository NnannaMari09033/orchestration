# tasks/models.py
from django.db import models
from django.conf import settings


class Project(models.Model):
    """
    Groups tasks under a project. Each project can have multiple members (users).
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        help_text="Users who are members of this project"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Represents a background task submitted by a user within a project.
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

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
        help_text="Optional: Assign this task to a project"
    )
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
