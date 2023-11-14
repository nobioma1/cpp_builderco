import uuid
import string
import random
from django.conf import settings
from django.db import models
from django.urls import reverse
from collections import OrderedDict
from guardian.shortcuts import assign_perm, get_perms, remove_perm


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
    def add_permissions(project, member_user, **kwargs):
        permissions = []

        is_creator = kwargs.get("is_creator", False)
        can_manage_project = kwargs.get("can_manage_project", False)
        can_manage_files = kwargs.get("can_manage_files", False)
        can_manage_members = kwargs.get("can_manage_members", False)

        if can_manage_project or is_creator:
            permissions += ['view_project', 'change_project', 'delete_project']
        else:
            permissions.append('view_project')

        if can_manage_files or is_creator:
            permissions.append('manage_files')

        if can_manage_members or is_creator:
            permissions.append('manage_members')

        print(permissions)

        # assign all project permissions
        for permission in permissions:
            assign_perm(permission, member_user, project)

        return True

    @staticmethod
    def remove_permissions(project, member_user):
        permissions = get_perms(member_user, project)

        for permission in permissions:
            remove_perm(permission, member_user, project)

        return True

    class Meta:
        db_table = "projects"
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]
        permissions = [
            ('manage_members', "Can add or remove members"),
            ('manage_files', "Can add or remove files")
        ]
