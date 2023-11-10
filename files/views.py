from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from projects.models import Project
from utils.aws_s3.s3 import S3

from .forms import UploadForm


def get_file_object_name(name, project_id):
    object_name = "_".join(name.split(" "))
    return f"projects/{project_id}/{object_name}"


# Create your views here.
def upload_file_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    form = UploadForm()

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data['file_name']
            file = request.FILES["file"]

            file_object_name = get_file_object_name(name, project_id)

            S3.upload_file(settings.AWS_STORAGE_BUCKET_NAME, file.file, object_name=file_object_name)

            return HttpResponseRedirect("/projects/")

    return render(request, template_name="files/file_upload.html", context={
        "form": form,
        "project": project
    })
