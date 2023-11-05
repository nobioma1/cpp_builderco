import logging
import boto3
from botocore.exceptions import ClientError


class DynamoDB:
    def __init__(self, region_name=None):
        self.resource = boto3.resource('dynamodb', region_name)
        self.region_name = region_name

    def create_table(self, name, key_schema, attribute_definitions, provisioned_throughput):
        try:
            table = self.resource.create_table(TableName=name, KeySchema=key_schema,
                                               AttributeDefinitions=attribute_definitions,
                                               ProvisionedThroughput=provisioned_throughput)

            table.meta.client.get_waiter('table_exists').wait(TableName=name)

        except ClientError as e:
            logging.error(e)
            raise

        return table
