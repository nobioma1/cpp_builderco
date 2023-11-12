import uuid
from django.conf import settings
from django.db import models
from collections import OrderedDict

from projects.models import Project


# Create your models here.
class Member(models.Model):
    MEMBER_ROLES = OrderedDict({
        "PM": "Project Manager",
        "ARCH": "Architect",
        "CE": "Civil Engineer",
        "SE": "Structural Engineer",
        "CM": "Construction Manager",
        "QS": "Quantity Surveyor",
        "SENG": "Site Engineer",
        "HSO": "Health and Safety Officer",
        "ELEC": "Electrician",
        "PLUM": "Plumber",
        "MAS": "Mason",
        "CARP": "Carpenter",
        "HEO": "Heavy Equipment Operator",
        "LS": "Land Surveyor",
        "EC": "Environmental Consultant",
        "ID": "Interior Designer",
        "MECHENG": "Mechanical Engineer",
        "ME": "Materials Engineer",
        "QC": "Quality Control",
        "INSPEC": "Inspector",
        "LANS": "Landscaper"
    })

    # Model Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=list(tuple(MEMBER_ROLES.items())))
    joined_at = models.DateTimeField(auto_now_add=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def get_role_value(self):
        return self.MEMBER_ROLES.get(self.role)

    class Meta:
        db_table = "project_members"
        ordering = ["joined_at"]
        verbose_name = "Member"
        verbose_name_plural = "Members"
        constraints = [
            models.UniqueConstraint(name='unique_project_user', fields=['project', 'user'])
        ]
