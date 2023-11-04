from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm, get_objects_for_user
from guardian.mixins import PermissionRequiredMixin

from .models import Project
from .form import ProjectForm


class ProjectCreateView(LoginRequiredMixin, CreateView):
    permission_required = "user.is_staff"
    template_name = 'projects/project_new.html'
    form_class = ProjectForm
    success_url = reverse_lazy('projects')

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        form.instance.identifier = Project.generate_identifier(form.instance.name)
        response = super().form_valid(form)

        content_type = ContentType.objects.get(app_label="projects")
        project_app_permissions = Permission.objects.filter(content_type=content_type)

        for permission in project_app_permissions:
            assign_perm(permission, self.request.user, self.object)

        return response


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Fetch projects where the current user has permission to view project
        return get_objects_for_user(self.request.user, "projects.view_project")


class ProjectDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Project
    permission_required = "projects.view_project"
    template_name = 'projects/project_detail.html'
