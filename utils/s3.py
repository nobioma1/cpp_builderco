import boto3
from django.conf import settings


class S3:
    @staticmethod
    def get_client(region=None):
        """ Initializes and returns an S3 client

        :param region: aws string name
        :return: s3_client
        """

        # use region argument or defined in settings config file
        region_name = region or settings.AWS_S3_BUCKET_REGION

        if not region_name:
            s3_client = boto3.client('s3')
        else:
            s3_client = boto3.client('s3', region_name=region_name)
        return s3_client

    @staticmethod
    def create_bucket(bucket_name, region=None):
        """Create an S3 bucket

        :param bucket_name: Bucket to create
        :param region: aws region to create bucket in
        :return: create_bucket response
        """

        # use region argument or defined in settings config file
        s3_client = S3.get_client(region)

        if not region:
            return s3_client.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': region}
            response = s3_client.create_bucket(Bucket=bucket_name,
                                               CreateBucketConfiguration=location)
            return response

    @staticmethod
    def enable_versioning(bucket_name, mfa_delete="Disabled"):
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

    @staticmethod
    def put_object(bucket, data, object_key):
        """Adds an object to an S3 bucket.

            :param data: bytes or seekable file-like object
            :param bucket: Bucket to upload to
            :param object_key: S3 object key. If not specified then file_name is used
            :return: response containing VersionID
        """

        s3_client = S3.get_client()
        response = s3_client.put_object(Body=data, Bucket=bucket, Key=object_key)
        return response

    @staticmethod
    def get_object(bucket_name, object_key):
        """Retrieves an object from an S3 bucket

        :param bucket_name: the name of the bucket
        :param object_key: the key of the object to retrieve
        :return: response or False
        """
        s3_client = S3.get_client()
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        return response

    @staticmethod
    def delete_object(bucket_name, key, version_id=None):
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
