from django.db import models
import uuid
from collections import OrderedDict

from projects.models import Project


# Create your models here.
class ProjectFile(models.Model):
    CATEGORIES = [
        "Budget and Financial Documents",
        "Contracts and Legal Documents",
        "Project Plans and Blueprints",
        "Material and Equipment Specifications",
        "Progress Reports and Logs",
        "Safety Plans and Compliance Documents",
        "Training Materials",
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField()
    name = models.CharField(max_length=255)
    category = models.CharField(choices=[(category, category) for category in CATEGORIES])
    created_at = models.DateTimeField(auto_now_add=True)
    versions = models.JSONField(default=dict)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_files')
