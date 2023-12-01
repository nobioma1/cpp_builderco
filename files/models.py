import uuid
import json
import datetime
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from projects.models import Project
from utils.sns import SNS


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
    name = models.CharField(max_length=100)
    category = models.CharField(choices=[(category, category) for category in CATEGORIES], max_length=150)
    versions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # `is_approved` is True if at least one version on the file is marked as approved
    is_approved = models.BooleanField(default=False)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_files')

    def __str__(self):
        return self.name

    def get_versions(self):
        return self.versions

    def get_versions_count(self):
        return len(self.get_versions())

    def approve_file(self):
        self.is_approved = True
        self.save()

        return True

    @staticmethod
    def add_file_version(version_id, user_id, versions=None):
        if versions is None:
            versions = list()

        versions.append({
            "id": version_id,
            "number": str(len(versions) + 1),
            "uploaded_by": str(user_id),
            "uploaded_at": str(datetime.datetime.now(datetime.UTC))
        })

        return versions

    class Meta:
        db_table = "project_files"
        verbose_name = "Project File"
        verbose_name_plural = "Project Files"
        ordering = ["-created_at"]


@receiver(pre_save, sender=ProjectFile)
def handle_notification_on_update(sender, instance, **kwargs):
    if instance.created_at:  # only execute block when it's an already existing record
        pre_save_instance = sender.objects.get(pk=instance.id)

        if not pre_save_instance.is_approved and instance.is_approved:
            project = instance.project
            notifications_to_send = ["FILE_APPROVED"]

            if not project.is_approved():
                pending_approval_files = sender.objects.filter(project=project, is_approved=False)
                pending_approval_len = len(pending_approval_files)

                if (pending_approval_len == 1 and pending_approval_files[0].id == instance.id
                        or pending_approval_len == 0):
                    notifications_to_send.append("ALL_FILES_APPROVED")

            for event_key in notifications_to_send:
                SNS.publish(json.dumps({
                    "EventType": event_key,
                    "Payload": {
                        "ProjectName": f"{project.name}({project.identifier})",
                        "FileName": instance.name,
                        "Category": instance.category,
                        "ProjectSubscriptionARN": project.project_subscription_arn,
                    }
                }))

            in_progress = "inprog"
            project.update_status(in_progress)
