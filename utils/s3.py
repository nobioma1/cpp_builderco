import boto3
import logging
from botocore.exceptions import ClientError


class S3:
    def __init__(self, region_name=None):
        self.client = boto3.client('s3', region_name)
        self.region_name = region_name

    def create_bucket(self, bucket_name, region=None, enable_versioning=False):
        """
            Create an S3 bucket

            :param bucket_name: Bucket name to created
            :param region: region to create bucket in
            :param enable_versioning: bool to enable bucket versioning

            :return: bool if bucket is created or not
        """

        create_bucket_configuration = dict()

        if region:
            create_bucket_configuration["LocationConstraint"] = self.region_name or region

        print(create_bucket_configuration)

        try:
            # Create s3 but with configurations
            self.client.create_bucket(Bucket=bucket_name,
                                      CreateBucketConfiguration=create_bucket_configuration)
            if enable_versioning:
                # enable versioning for created bucket
                self.enable_versioning(bucket_name)

        except ClientError as err:
            logging.error(err)
            raise

        return True

    def enable_versioning(self, bucket_name, mfa_delete="Disabled"):
        """

        :param bucket_name: bucket name to enable versioning on.
        :param mfa_delete: 'Disabled' or 'Enabled'
        :return: bool depending on success
        """
        try:
            # enable versioning for bucket with name
            self.client.put_bucket_versioning(Bucket=bucket_name,
                                              VersioningConfiguration={
                                                  'MFADelete': mfa_delete,
                                                  'Status': 'Enabled',
                                              })
        except ClientError as err:
            logging.error(err)
            raise

        return True
