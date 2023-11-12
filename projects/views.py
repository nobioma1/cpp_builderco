from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm, get_objects_for_user
from functools import wraps
from django.shortcuts import render, get_object_or_404
from guardian.decorators import permission_required
from django.contrib.auth.decorators import login_required

from .models import Project
from .form import ProjectForm


def get_project_or_404(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get 'project_id' or 'pk' passed via kwargs or URL
        project_id = kwargs.get('project_id') or kwargs.get('pk') or request.GET.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        # Pass project to view
        kwargs['project'] = project

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@login_required
def project_list_view(request):
    # Fetch projects where the current user has permission to view project
    projects = get_objects_for_user(request.user, "projects.view_project")

    return render(request, 'projects/project_list.html', {
        'projects': projects,
    })


@login_required
@permission_required('projects.view_project')
@get_project_or_404
def project_detail_view(request, pk, **kwargs):
    return render(request, 'projects/project_detail.html', {
        'project': kwargs.get('project'),
    })


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
