from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView

from .models import Project


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
