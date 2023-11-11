from django.db import models
import uuid
import datetime

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

    def __str__(self):
        return self.name

    class Meta:
        db_table = "project_files"
        verbose_name = "Project File"
        verbose_name_plural = "Project Files"
        ordering = ["created_at"]

    @staticmethod
    def add_file_version(version_id, user_id, versions=None):
        if versions is None:
            versions = dict({"file_versions": list()})

        versions["file_versions"].append({
            "id": version_id,
            "uploaded_by": str(user_id),
            "uploaded_at": str(datetime.datetime.now(datetime.UTC))
        })

        return versions

