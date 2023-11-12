from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required

from projects.views import get_project_or_404

from .backends.s3 import S3Storage
from .form import ProjectFileForm
from .models import ProjectFile


# Create your views here.
@login_required
@permission_required('projects.view_project')
@get_project_or_404
def project_files_list(request, **kwargs):
    project = kwargs.get('project')
    project_files = ProjectFile.objects.filter(project_id=project)

    return render(request, template_name="files/project_files.html", context={
        "files": project_files,
        "project": project
    })


@login_required
@permission_required('projects.view_project')
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

            return HttpResponseRedirect("/projects/" + str(project.id) + "/files")

    return render(request, template_name="files/file_upload.html", context={
        "form": form,
        "project": project
    })
