import os
from django.core.files.storage import Storage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import datetime

from utils.aws_s3.s3 import S3


class S3Storage(Storage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def generate_object_key(file, name, project_id):
        _, file_ext = os.path.splitext(file.name)
        concat_name = "_".join(name.split(" "))
        return f"projects/{project_id}/{concat_name}{file_ext}"

    # Uploading directly to s3 using the "s3_client.upload_file" throws an error
    # "Filename must be a string or a path-like object"
    # workaround: first write uploaded file to disk then use s3_client.upload_obj
    def _save(self, name, content):
        # write uploaded file to temp folder on disk
        file_path = default_storage.save(
            'tmp-files/' + content.name + str(datetime.datetime.now(datetime.UTC)),
            ContentFile(content.read()))
        # get path to uploaded file
        full_file_path = os.path.join(default_storage.location, file_path)

        try:
            # read uploaded temp-file and upload to s3 using the upload_fileobj method on the client
            with open(full_file_path, 'rb') as data:
                uploaded = S3.upload_file(settings.AWS_STORAGE_BUCKET_NAME, data, object_key=name)

                if not uploaded:
                    raise Exception("Error uploading file")
        finally:
            # delete temp file from disk
            default_storage.delete(file_path)

        return name

    def exists(self, name):
        return False
