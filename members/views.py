from django.shortcuts import render
from guardian.decorators import permission_required
from django.contrib.auth.decorators import login_required

from projects.views import get_project_or_404

from .models import Member


# Create your views here.
@login_required
@permission_required('projects.view_project')
@get_project_or_404
def list_members_view(request, **kwargs):
    project = kwargs.get('project')
    project_members = Member.objects.filter(project=project)

    return render(request, template_name="members/list_members.html", context={
        "project": project,
        "members": project_members
    })
