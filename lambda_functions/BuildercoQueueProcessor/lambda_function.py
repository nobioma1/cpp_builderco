import boto3
import ast
from cpp_aws_s3_pdf.s3_pdf import S3Pdf

session = boto3.session.Session()

s3_client = session.client("s3")
sns_client = session.client("sns")


def lambda_handler(event, context):
    print("running lambda function for {} records".format(len(event['Records'])))

    for record in event["Records"]:
        body = ast.literal_eval(record['body'])

        if "EventType" in body:
            bucket_name = "builder-co-prod"
            event_type = body["EventType"]
            payload = body["Payload"]

            print(f"Handling event for {event_type}")

            # On "MERGE_FILES":
            # - use AWS_S3_PDF package to merge files and send url to initiator
            if event_type == "MERGE_FILES":
                print("merging objects {}".format(payload["FileObjectKeys"]))
                s3_pdf = S3Pdf(bucket_name="builderco-artifacts")
                download_url = s3_pdf.combine_objects(payload["FileObjectKeys"])
                sns_client.publish(
                    TopicArn=payload["NotifySubscriptionARN"],
                    Subject="Project Files Merged",
                    Message="Project had been merged, download link expires in 60 minutes. Click url to download {}".format(
                        download_url))
                print("Files merged successfully")

            # On "PROCESS_FILE_WATERMARK":
            # - use AWS_S3_PDF package to apply watermark on uploaded object
            if event_type == "PROCESS_FILE_WATERMARK":
                print("Watermarking {}".format(payload["ObjectKey"]))
                s3_pdf = S3Pdf(bucket_name=bucket_name)
                s3_pdf.apply_watermark_object(payload["ObjectKey"], text=payload["WatermarkText"])
                print("Watermark applied successfully")

            # On "PROJECT_DELETED":
            # - set delete marker project files in S3
            # - delete project SNS topic
            if event_type == "PROJECT_DELETED":
                print('Deleting project data - {}'.format(payload["ProjectId"]))

                # delete project sns topic
                print("Deleting sns project topic")
                sns_res = sns_client.delete_topic(TopicArn=payload["ProjectSubscriptionARN"])
                print("sns delete response", sns_res)

                # delete project file objects and versions
                objects_to_delete = payload["ObjectsToDelete"]
                print("Deleting s3 objects - ", len(objects_to_delete))
                s3_delete_res = s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={
                        'Quiet': True,
                        'Objects': objects_to_delete,
                    }
                )
                print("s3 delete response", s3_delete_res)

    return {'statusCode': 200}
