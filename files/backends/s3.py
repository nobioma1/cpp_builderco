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

    def _save(self, name, content):
        response = S3.put_object(settings.AWS_STORAGE_BUCKET_NAME, content, object_key=name)

        if response is None:
            raise Exception("Error uploading file")

        return response["VersionId"]

    def exists(self, name):
        return False
