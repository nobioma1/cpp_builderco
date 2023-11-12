from django.core.management.base import BaseCommand, CommandError
from botocore.exceptions import ClientError
from django.conf import settings

from utils.dynamodb import DynamoDB


# usage
# python manage.py create_files_dynamodb_table

class Command(BaseCommand):
    help = "Create Dynamodb Table to store project files metadata"

    def handle(self, *args, **options):
        dynamodb = DynamoDB(region_name=settings.AWS_REGION)

        table_name = "project_files"

        key_schema = [
            {
                "AttributeName": "file_id",
                "KeyType": "HASH"
            },
            {
                'AttributeName': 'project_id',
                'KeyType': 'RANGE'
            }
        ]

        attribute_definitions = [
            {
                "AttributeName": "file_id",
                "AttributeType": "S"
            },
            {
                "AttributeName": "project_id",
                "AttributeType": "S"
            }

        ]

        provisioned_throughput = {
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }

        try:
            dynamodb.create_table(table_name, key_schema, attribute_definitions, provisioned_throughput)
            self.stdout.write(self.style.SUCCESS(f'Successfully created table "{table_name}"'))
        except ClientError as e:
            raise CommandError('Error executing create_table', e)
