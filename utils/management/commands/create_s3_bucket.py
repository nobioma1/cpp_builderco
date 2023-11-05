from django.core.management.base import BaseCommand, CommandError
from botocore.exceptions import ClientError

from utils.s3 import S3


# usage
# python manage.py create_s3_bucket --name bucket-name --region us-west-2 --enable_versioning

class Command(BaseCommand):
    help = "Creates an AWS S3 bucket in specified region and enabling versioning"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, help="bucket name to be created")
        parser.add_argument("--region", type=str, help="bucket region to be created in")
        parser.add_argument("--enable_versioning", action="store_true", help="bucket name to be created")

    def handle(self, *args, **options):

        bucket_name = options["name"]
        bucket_region = options["region"]
        enable_versioning = options["enable_versioning"]

        s3 = S3(region_name=bucket_region)

        try:
            s3.create_bucket(bucket_name, region=bucket_region, enable_versioning=enable_versioning)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created bucket "{bucket_name}"" in "{bucket_region}", versioning: {enable_versioning}')
            )
        except ClientError as e:
            raise CommandError('Error executing create_s3_bucket', e)
