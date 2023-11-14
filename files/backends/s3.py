import os
from django.core.files.storage import Storage
from django.conf import settings
from botocore.exceptions import ClientError

from utils.s3 import S3


class S3Exception(Exception):
    def __init__(self, message="Something went wrong", error=None):
        self.message = message
        self.error = error


class UploadException(S3Exception):
    """Exception when upload fails"""

    def __init__(self, message="Error uploading file", error=None):
        self.message = message
        self.error = error
        super().__init__(self.message)

    def __str__(self):
        return self.message


class S3Storage(Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_url_path(project_id):
        return f"projects/{project_id}"

    @staticmethod
    def generate_object_key(file, name, project_id):
        _, file_ext = os.path.splitext(file.name)
        concat_name = "_".join(name.split(" "))
        url_path = S3Storage.get_url_path(project_id)
        return f"{url_path}/{concat_name}{file_ext}"

    def _save(self, name, content):
        try:
            response = S3.put_object(self.bucket_name, content, object_key=name)
            return response["VersionId"]
        except ClientError as err:
            raise UploadException(error=err)

    def delete(self, name, version_id=None):
        try:
            S3.delete_object(self.bucket_name, name, version_id)
            return True
        except ClientError as err:
            raise S3Exception(error=err)

    def exists(self, name):
        return False
