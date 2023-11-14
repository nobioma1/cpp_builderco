from django.shortcuts import render, redirect
from guardian.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
import uuid

from projects.views import get_project_or_404
from projects.models import Project

from .models import Member
from .form import ProjectMemberForm

User = get_user_model()


# Create your views here.
@login_required
@permission_required('projects.view_project', (Project, 'id', 'project_id'))
@get_project_or_404
def list_or_manage_members_view(request, **kwargs):
    project = kwargs.get('project')
    project_perms = kwargs.get('project_perms')
    project_members = Member.objects.filter(project=project)
    can_manage_members = "manage_members" in project_perms

    if request.method == "POST" and can_manage_members:
        if 'remove' in request.POST:
            value = request.POST["remove"]

            try:
                # Validate and normalize expected uuid value
                member_to_remove_id = str(uuid.UUID(value.rstrip("/")))

                # is member id valid
                member = project_members.get(id=member_to_remove_id)
                # remove member from project
                project.remove_member_from_project(member)

                return redirect("/projects/" + str(project.id) + "/members")
            except ObjectDoesNotExist:
                # handle error or log
                pass
            except ValueError:
                # handle error or log
                pass

    return render(request, template_name="members/list_or_manage_members.html", context={
        "project": project,
        "members": project_members,
        "can_manage_members": can_manage_members,
    })


@login_required
@permission_required('projects.manage_members', (Project, 'id', 'project_id'))
@get_project_or_404
def add_members_view(request, **kwargs):
    project = kwargs.get('project')
    form = ProjectMemberForm()

    if request.method == "POST":
        form = ProjectMemberForm(request.POST)

        if form.is_valid():
            user_email = form.cleaned_data["user_email"]

            try:
                user_to_be_member = User.objects.get(email=user_email)
                is_member = Member.objects.filter(user=user_to_be_member, project=project).exists()

                if is_member:
                    form.add_error("user_email", "Invalid email, user is already a member")
                else:
                    can_manage_members = form.cleaned_data["can_manage_members"]
                    can_manage_files = form.cleaned_data["can_manage_files"]
                    can_manage_project = form.cleaned_data["can_manage_project"]

                    # create member instance
                    member = Member.objects.create(user=user_to_be_member,
                                                   project=project,
                                                   role=form.cleaned_data["role"])

                    # add user to project with permissions
                    project.add_member_to_project(member,
                                                  can_manage_members=can_manage_members,
                                                  can_manage_files=can_manage_files,
                                                  can_manage_project=can_manage_project)

                    return redirect("/projects/" + str(project.id) + "/members")

            except ObjectDoesNotExist:
                form.add_error("user_email", "Invalid email, user is not registered")

    return render(request, template_name="members/add_member.html", context={
        "project": project,
        "form": form,
    })
