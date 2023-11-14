from django.conf import settings

from .aws import AWS


class S3(AWS):
    service_name = 's3'

    @classmethod
    def create_bucket(cls, bucket_name, region=None):
        """Create an S3 bucket

        :param bucket_name: Bucket to create
        :param region: aws region to create bucket in
        :return: create_bucket response
        """

        # use region argument or defined in settings config file
        client_region = region or settings.AWS_S3_BUCKET_REGION
        s3_client = S3.get_client(client_region)

        if not region:
            return s3_client.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': region}
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
