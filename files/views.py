from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from projects.models import Project

from .form import ProjectFileForm
from .backends.s3 import S3Storage


# Create your views here.
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
            file_key = storage.save(file_name, file)

            # update model fields
            form.instance.project = project
            form.instance.uploaded_by = request.user
            form.instance.file = file_key

            form.save()  # saving file to db

            return HttpResponseRedirect("/projects/")

    return render(request, template_name="files/file_upload.html", context={
        "form": form,
        "project": project
    })
