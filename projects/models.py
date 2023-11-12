import uuid
import string
import random
from django.conf import settings
from django.db import models
from django.urls import reverse
from collections import OrderedDict
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm


class Project(models.Model):
    PROJECT_STATUS = OrderedDict({
        "pendin": "Pending",
        "inprog": "In Progress",
        "comptd": "Completed"
    })

    PROJECT_TYPE = OrderedDict({
        "com": "Commercial",
        "res": "Residential",
        "ind": "Industrial"
    })

    # Model Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    type = models.CharField(max_length=3, choices=list(tuple(PROJECT_TYPE.items())))
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=6, default="pendin", choices=list(tuple(PROJECT_STATUS.items())))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project', args=[self.id])

    def get_status(self):
        return self.PROJECT_STATUS.get(self.status)

    def get_type(self):
        return self.PROJECT_TYPE.get(self.type)

    @staticmethod
    def generate_identifier(name):
        """
        generate an identifier of concatenated strings

        :param name: name of project to be created
        :return: identifier string
        """
        unique_id = str(uuid.uuid4().hex)[:10]
        words = name.upper().split(" ")
        max_len = 4

        # ensure word are at least 4 characters(max_len)
        if len(words) < max_len:
            for _ in range(0, max_len - len(words)):
                words.append(random.choice(string.ascii_uppercase))

        # ensure character is a valid uppercase character
        for idx, word in enumerate(name.split(" ")):
            char = word[0]
            if ord(char) < 65 or ord(char) > 90:
                words[idx] = random.choice(string.ascii_uppercase)
            else:
                words[idx] = char

        return f"{''.join(words)}-{unique_id.upper()}"

    @staticmethod
    def assign_permissions(user, project, permission=None, is_creator=False):
        permissions = []

        if is_creator:
            # get permission content types
            content_types = ContentType.objects.filter(app_label="projects")
            # get project permissions
            permissions = Permission.objects.filter(content_type__in=content_types)
        else:
            permission = Permission.objects.get(content_type__permission=permission)
            permissions.append(permission)

        # assign all project permissions to creator
        for permission in permissions:
            assign_perm(permission, user, project)

        return True

    class Meta:
        db_table = "projects"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]
