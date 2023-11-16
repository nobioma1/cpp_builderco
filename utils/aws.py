import boto3
from django.conf import settings


class AWS:
    service_name = None
    region = None

    @classmethod
    def get_client(cls, region=None):
        """ Initializes and returns an S3 client

        :param region: aws string name
        :return: s3_client
        """

        if not cls.service_name:
            raise ValueError("invalid service name")

        region_name = cls.region or region

        if not region_name:
            client = boto3.client(cls.service_name)
        else:
            client = boto3.client(cls.service_name, region_name=region_name)
        return client
