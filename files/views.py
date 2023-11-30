from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from utils.sns import SNS
import json
# from cpp_aws_s3_pdf.files import S3ToPDFCombine

from projects.views import get_project_or_404
from projects.models import Project

from .backends.s3 import S3Storage, UploadException
from .form import ProjectFileForm
from .models import ProjectFile


def sort_project_files_categories(project_files):
    sorted_by_category = dict()

    for file in project_files:
        category_in_dict = sorted_by_category.get(file.category, None)
        if category_in_dict is None:
            sorted_by_category[file.category] = [file]
        else:
            category_in_dict.append(file)

    return sorted_by_category


# Create your views here.
@login_required
@permission_required('projects.view_project', (Project, 'id', 'project_id'))
@get_project_or_404
def project_files_list(request, **kwargs):
    """List project files, Approve project files and Send Notification for files merge"""

    project = kwargs.get('project')
    project_perms = kwargs.get('project_perms')
    project_files = ProjectFile.objects.filter(project_id=project)
    sorted_project_files = sort_project_files_categories(project_files)

    messages.error(request, "File format in files not supported, only pdfs.")

    if request.method == 'POST':
        # handle request to approval a file
        if 'approved' in request.POST and 'review_files' in project_perms:
            file_id_to_approve = str(request.POST["approved"]).rstrip("/")
            file = project_files.get(pk=file_id_to_approve)
            file.approve_file()

            SNS.publish(SNS.app_arn, json.dumps({
                "EventType": "FILE_APPROVED",
                "payload": {
                    "Project": project.name,
                    "FileName": file.name,
                    "Category": file.category,
                    "User": request.user.get_full_name(),
                    "ProjectSubscriptionARN": project.project_subscription_arn,
                }
            }))

            return redirect(f"/projects/{str(project.id)}/files")

        # handle request to merge files
        if 'merged' in request.POST and 'manage_files' in project_perms:
            pass
            # storage = S3Storage()
            #
            # files_object_keys = [str(file.file) for file in project_files]
            # try:
            #     download_url = storage.merge_objects(files_object_keys)
            #     return HttpResponseRedirect(download_url)
            # except UnsupportedFileTypeException:
            #     messages.error(request, "File format in files not supported, only pdfs.")
            # except S3PDFCombineException:
            #     messages.error(request, "Something went wrong please try again, only pdfs are supported in merge")

    return render(request, template_name="files/project_files.html", context={
        "files": project_files,
        "project": project,
        "category_project_files": sorted_project_files.items(),
        "can_manage_files": 'manage_files' in project_perms
    })


@login_required
@permission_required('projects.manage_files', (Project, 'id', 'project_id'))
@get_project_or_404
def upload_file_view(request, **kwargs):
    """Upload a new file version"""

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
                    object_key = storage.generate_object_key(file, name, project.id)
                    version_id = storage.save(object_key, file)
                    # set form fields
                    form.instance.file = object_key
                    form.instance.versions = ProjectFile.add_file_version(version_id, request.user.id)

                form.save()
                SNS.publish(SNS.app_arn, json.dumps({
                    "EventType": "NEW_VERSION_UPLOAD",
                    "payload": {
                        "Project": project.name,
                        "FileName": name,
                        "Category": form.instance.category,
                        "User": request.user.get_full_name(),
                        "Version": len(form.instance.versions),
                        "ProjectSubscriptionARN": project.project_subscription_arn,
                    }
                }))

                return redirect(f"/projects/{str(project.id)}/files")

            except UploadException as e:
                print(e)
                form.add_error(None, "Error uploading file, please try again!")

    return render(request, template_name="files/file_upload.html", context={
        "form": form,
        "project": project
    })


@login_required
@permission_required('projects.view_project', (Project, 'id', 'project_id'))
@get_project_or_404
def list_file_versions(request, **kwargs):
    """List file versions"""

    project = kwargs.get('project')
    project_perms = kwargs.get('project_perms')
    file = get_object_or_404(ProjectFile, id=kwargs.get('file_id'))
    versions = file.get_versions()

    can_manage_files = 'manage_files' in project_perms

    if request.method == 'POST':
        storage = S3Storage()

        # handle request to delete a file version
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

            return redirect(f"/projects/{str(project.id)}/files")

    return render(request, template_name="files/list_versions.html", context={
        "project": project,
        "file": file,
        "versions": versions[::-1],
        "can_manage_files": 'manage_files' in project_perms
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

# TODO: Using SQS queue project clean up when a project is deleted (removing SNS subscription, deleting s3 data) by sending SNS notification.
# TODO: Integrate cloudwatch for logging in the code and the lambda function
# TODO: add functionality to update project status when blueprint is approved and freeze blueprints upload, notify everyone on approval
