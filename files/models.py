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
    versions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_files')

    def __str__(self):
        return self.name

    def get_versions(self):
        return self.versions["file_versions"]

    def get_versions_count(self):
        return len(self.versions["file_versions"])

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

    class Meta:
        db_table = "project_files"
        verbose_name = "Project File"
        verbose_name_plural = "Project Files"
        ordering = ["-created_at"]



