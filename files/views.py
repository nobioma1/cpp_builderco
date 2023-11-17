from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
from django.http import HttpResponseRedirect

from projects.views import get_project_or_404
from projects.models import Project

from .backends.s3 import S3Storage, UploadException
from .form import ProjectFileForm
from .models import ProjectFile


# Create your views here.
@login_required
@permission_required('projects.view_project', (Project, 'id', 'project_id'))
@get_project_or_404
def project_files_list(request, **kwargs):
    project = kwargs.get('project')
    project_files = ProjectFile.objects.filter(project_id=project)
    project_perms = kwargs.get('project_perms')

    return render(request, template_name="files/project_files.html", context={
        "files": project_files,
        "project": project,
        "can_manage_files": 'manage_files' in project_perms
    })


@login_required
@permission_required('projects.manage_files', (Project, 'id', 'project_id'))
@get_project_or_404
def upload_file_view(request, **kwargs):
    project = kwargs.get('project')
    form = ProjectFileForm(project=project)

    if request.method == "POST":
        form = ProjectFileForm(request.POST, request.FILES, project=project)

        if form.is_valid():
            storage = S3Storage()  # initialize S3 storage to be used for file upload

            file = request.FILES['file']
            name = form.cleaned_data['name']
            is_new_version = form.cleaned_data["is_new_version"]
            existing_file_id = form.cleaned_data["existing_file"]

            project_file = None

            if existing_file_id is not None and is_new_version:
                project_file = ProjectFile.objects.get(pk=existing_file_id)

            try:
                # if project_file, update existing file versions
                if project_file:
                    form.instance = project_file
                    # use an existing file name to upload a new version to s3
                    version_id = storage.save(project_file.file, file)
                    form.instance.versions = ProjectFile.add_file_version(version_id,
                                                                          request.user.id,
                                                                          project_file.versions)
                # else, create a new file record
                else:
                    form.instance.project = project
                    # handle file upload to s3 for new file and version
                    file_name = storage.generate_object_key(file, name, project.id)
                    version_id = storage.save(file_name, file)
                    # set form fields
                    form.instance.file = file_name
                    form.instance.versions = ProjectFile.add_file_version(version_id, request.user.id)

                form.save()

                return redirect("/projects/" + str(project.id) + "/files")

            except UploadException:
                form.add_error(None, "Error uploading file, please try again!")

    return render(request, template_name="files/file_upload.html", context={
        "form": form,
        "project": project
    })


@login_required
@permission_required('projects.view_project', (Project, 'id', 'project_id'))
@get_project_or_404
def list_file_versions(request, **kwargs):
    project = kwargs.get('project')
    project_perms = kwargs.get('project_perms')
    file = get_object_or_404(ProjectFile, id=kwargs.get('file_id'))
    versions = file.get_versions()

    can_manage_files = 'manage_files' in project_perms

    if request.method == 'POST':
        storage = S3Storage()

        if 'delete_version' in request.POST and can_manage_files:
            file_key = str(file.file)

            if len(versions) == 1:
                storage.delete(file_key)
                file.delete()
            else:
                version_id_to_be_deleted = str(request.POST["delete_version"]).rstrip("/")
                file.versions = [version for version in versions if version.get("id") != version_id_to_be_deleted]
                storage.delete(file_key, version_id_to_be_deleted)
                file.save()

            return redirect("/projects/" + str(project.id) + "/files")

    return render(request, template_name="files/list_versions.html", context={
        "project": project,
        "file": file,
        "versions": versions[::-1]
    })


@login_required
@permission_required('projects.view_project', (Project, 'id', 'project_id'))
@get_project_or_404
def get_file_version(request, **kwargs):
    version_id = request.GET.get('v', '')
    file = get_object_or_404(ProjectFile, id=kwargs.get('file_id'))
    versions = file.get_versions()

    if not version_id:
        # assign the version id of the last version to "version_id"
        version_id = versions[-1]["id"]

    storage = S3Storage()
    file_version_url = storage.download_version(str(file.file), version_id)
    return HttpResponseRedirect(file_version_url)

# TODO: trigger lambda function "new_file_version_upload" when a new object is added in the s3 bucket get the project id from file path.
# TODO: Send email using an SNS when a user is added to a project
# TODO: Using SQS queue project clean up when a project is deleted (removing SNS subscription, deleting s3 data) by sending SNS notification.
# TODO: what is the library?
