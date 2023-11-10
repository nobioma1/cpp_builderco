from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
import datetime

from projects.models import Project

from .backends.s3 import S3Storage
from .form import ProjectFileForm
from .models import ProjectFile


# Create your views here.
@login_required
@permission_required('projects.view_project')
def project_files_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_files = ProjectFile.objects.filter(project_id=project)

    return render(request, template_name="files/project_files.html", context={
        "files": project_files,
        "project": project
    })


@login_required
@permission_required('projects.view_project')
def upload_file_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    form = ProjectFileForm()

    if request.method == "POST":
        form = ProjectFileForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data['name']
            file = request.FILES['file']

            # handle file upload to s3
            storage = S3Storage()
            file_name = storage.generate_object_key(file, name, project.id)
            version_id = storage.save(file_name, file)

            print(version_id)

            # update model fields
            form.instance.project = project
            form.instance.file = file_name

            # add version metadata
            versions = dict({"file_versions": list()})
            versions["file_versions"].append({
                "id": version_id,
                "uploaded_by": str(request.user.id),
                "uploaded_at": str(datetime.datetime.now(datetime.UTC))
            })
            form.instance.versions = versions

            # save form to db
            form.save()

            return HttpResponseRedirect("/projects/" + str(project_id) + "/files")

    return render(request, template_name="files/file_upload.html", context={
        "form": form,
        "project": project
    })
