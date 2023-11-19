from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from guardian.shortcuts import get_objects_for_user, get_perms
from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from guardian.decorators import permission_required
from django.contrib.auth.decorators import login_required

from members.models import Member
from files.backends.s3 import S3Storage, S3Exception
from utils.sns import SNS

from .models import Project
from .form import ProjectForm


def get_project_or_404(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get 'project_id' or 'pk' passed via kwargs or URL
        project_id = kwargs.get('project_id') or kwargs.get('pk') or request.GET.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        # get user object permissions
        user_project_perms = get_perms(request.user, project)

        # Pass project to view
        kwargs['project'] = project
        kwargs['project_perms'] = user_project_perms

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
@permission_required('projects.view_project', (Project, 'id', 'pk'))
@get_project_or_404
def project_detail_view(request, **kwargs):
    return render(request, 'projects/project_detail.html', {
        'project': kwargs.get('project'),
    })


@login_required
@permission_required('projects.view_project', (Project, 'id', 'pk'))
@get_project_or_404
def project_manage_view(request, **kwargs):
    project = kwargs.get('project')
    project_perms = kwargs.get('project_perms')
    form = ProjectForm(instance=project)

    # get user object permissions
    can_change_project = 'change_project' in project_perms
    can_delete_project = 'delete_project' in project_perms

    if request.method == 'POST':
        if 'delete' in request.POST and can_delete_project:
            # delete project
            project.delete()
            try:
                s3 = S3Storage()
                s3.delete(s3.get_url_path(project.id))
            except S3Exception:
                # send it to logs
                pass
            return redirect('projects')

        if can_change_project:
            # update project
            form = ProjectForm(request.POST, instance=project)

            if form.is_valid():
                form.save()
                return redirect('project', pk=str(project.id))

    return render(request, 'projects/project_manage.html', {
        'project': project,
        'form': form,
        'can_change_project': can_change_project,
        'can_delete_project': can_delete_project,
        'can_manage_project': can_change_project or can_delete_project
    })


class ProjectCreateView(LoginRequiredMixin, CreateView):
    permission_required = "user.is_staff"
    template_name = 'projects/project_new.html'
    form_class = ProjectForm
    success_url = reverse_lazy('projects')

    def form_valid(self, form):
        user = self.request.user

        # update form fields for model
        form.instance.user = user
        form.instance.identifier = Project.generate_identifier(form.instance.name)

        response = super().form_valid(form)

        instance = form.save(commit=False)

        # create SNS topics users can subscribe to
        topic_arn = SNS.create_topic(name="project-" + str(self.object.id))
        # update project to add the topic arn
        instance.project_subscription_arn = topic_arn
        form.save()

        # add self to sns topic
        subscription_arn = SNS.subscribe(topic_arn, "email", user.email)

        # add user to project and assign permissions
        # add user to project members
        member = Member.objects.create(project=self.object, user=user, role="PM", subscription_arn=subscription_arn)
        self.object.add_member_to_project(member, is_creator=True)

        return response
