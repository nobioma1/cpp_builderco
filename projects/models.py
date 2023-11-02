from django.conf import settings
from django.db import models
from django.urls import reverse
from collections import OrderedDict
import uuid


class Project(models.Model):
    PENDING = "0"
    IN_PROGRESS = "1"
    COMPLETED = "2"

    PROJECT_STATUS = OrderedDict({
        PENDING: "Pending",
        IN_PROGRESS: "In Progress",
        COMPLETED: "Completed"
    })

    # Model Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=2,
        default=PENDING,
        choices=list(tuple(PROJECT_STATUS.items()))
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.project_name

    def get_absolute_url(self):
        return reverse('project', args=[self.id])

    def get_status_value(self):
        return self.PROJECT_STATUS.get(self.status)

    class Meta:
        db_table = "projects"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["created_at"]
