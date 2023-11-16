from django.core.management.base import BaseCommand, CommandError
from botocore.exceptions import ClientError
from django.conf import settings

from utils.s3 import S3


# usage
# python manage.py create_s3_bucket --name builder-co --enable_versioning

class Command(BaseCommand):
    help = "Creates an AWS S3 bucket in specified region and enabling versioning"

    def add_arguments(self, parser):
        name = settings.AWS_STORAGE_BUCKET_NAME or None

        parser.add_argument("--name", type=str, default=name, help="bucket name to be created")
        parser.add_argument("--enable_versioning", action="store_true", help="bucket name to be created")

    def handle(self, *args, **options):

        bucket_name = options["name"]
        enable_versioning = options["enable_versioning"]

        try:
            response = S3.create_bucket(bucket_name)

            if response and enable_versioning:
                S3.enable_versioning(bucket_name)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created bucket "{bucket_name}"" in "{S3.region}", versioning: {enable_versioning}')
            )
        except ClientError as e:
            raise CommandError('Error executing create_s3_bucket', e)
