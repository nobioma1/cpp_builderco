from django.conf import settings

from .aws import AWS


class S3(AWS):
    service_name = 's3'
    region = settings.AWS_S3_BUCKET_REGION

    @classmethod
    def create_bucket(cls, bucket_name, location_constraint_region=None):
        """Create an S3 bucket

        :param bucket_name: Bucket to create
        :param location_constraint_region
        :return: create_bucket response
        """

        s3_client = S3.get_client()

        if not location_constraint_region:
            return s3_client.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': location_constraint_region}
            response = s3_client.create_bucket(Bucket=bucket_name,
                                               CreateBucketConfiguration=location)
            return response

    @classmethod
    def enable_versioning(cls, bucket_name, mfa_delete="Disabled"):
        """Enable versioning on an existing bucket

        :param bucket_name: bucket name to enable versioning on.
        :param mfa_delete: 'Disabled' or 'Enabled'
        :return: bool depending on success
        """
        s3_client = S3.get_client()

        # enable versioning for bucket with name
        s3_client.put_bucket_versioning(Bucket=bucket_name,
                                        VersioningConfiguration={
                                            'MFADelete': mfa_delete,
                                            'Status': 'Enabled',
                                        })
        return True

    @classmethod
    def put_object(cls, bucket, data, object_key):
        """Adds an object to an S3 bucket.

            :param data: bytes or seekable file-like object
            :param bucket: Bucket to upload to
            :param object_key: S3 object key. If not specified then file_name is used
            :return: response containing VersionID
        """

        s3_client = S3.get_client()
        response = s3_client.put_object(Body=data, Bucket=bucket, Key=object_key)
        return response

    @classmethod
    def get_object(cls, bucket_name, object_key):
        """Retrieves an object from an S3 bucket

        :param bucket_name: the name of the bucket
        :param object_key: the key of the object to retrieve
        :return: response or False
        """
        s3_client = S3.get_client()
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response

    @classmethod
    def delete_object(cls, bucket_name, key, version_id=None):
        """
        Remove object or version from s3 (delete marker using versioning)

        :param bucket_name:  the name of the bucket
        :param key: the key of the object to delete
        :param version_id: version of object to delete
        :return:
        """
        s3_client = S3.get_client()

        kwargs = dict()
        kwargs["Bucket"] = bucket_name
        kwargs["Key"] = key

        if version_id is not None:
            kwargs["VersionId"] = version_id

        response = s3_client.delete_object(**kwargs)

        return response

    @classmethod
    def generate_download_url(cls, bucket_name, object_key, version_id, expiration=3600):
        """
        Generate a pre-signed url for an S3 object with a specific version.

        :param bucket_name: Name of the S3 bucket.
        :param object_key: Key of the S3 object.
        :param version_id: Version ID of the S3 object.
        :param expiration: Time in seconds for the pre-signed url to remain valid, defaults to 1hr.
        :return: pre-signed url as a string.
        """
        s3_client = S3.get_client()

        params = {'Bucket': bucket_name,
                  'Key': object_key,
                  'VersionId': version_id}

        pre_signed_url = s3_client.generate_presigned_url('get_object',
                                                          Params=params,
                                                          ExpiresIn=expiration)
        return pre_signed_url
