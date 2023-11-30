import boto3
import ast

s3 = boto3.client('s3')
sns = boto3.client('sns')


def lambda_handler(event, context):
    print("running lambda function - ", len(event['Records']))

    for record in event['Records']:
        if "Sns" in record:
            print("Evaluating SNS message")
            event_payload = ast.literal_eval(record['Sns']['Message'])

            # On "NEW_VERSION_UPLOAD" send Project SNS notification
            if event_payload['EventType'] == "NEW_VERSION_UPLOAD":
                print('Publishing SNS "NEW_VERSION_UPLOAD" notification')
                sns.publish(
                    TopicArn=event_payload["payload"]["ProjectSubscriptionARN"],
                    Message="A new file version({} - v{}) has been uploaded for {} by {}. Login to Builderco to view file in project {}.".format(
                        event_payload["payload"]["FileName"],
                        event_payload["payload"]["Version"],
                        event_payload["payload"]["Category"],
                        event_payload["payload"]["User"],
                        event_payload["payload"]["Project"]),
                    Subject="{} - New File Version Uploaded".format(event_payload["payload"]["Project"])
                )

            # On "FILE_APPROVED" send Project SNS notification
            if event_payload['EventType'] == "FILE_APPROVED":
                print('Publishing SNS "FILE_APPROVED" notification')
                sns.publish(
                    TopicArn=event_payload["payload"]["ProjectSubscriptionARN"],
                    Message="{}({}) has been approved by {}.".format(
                        event_payload["payload"]["FileName"],
                        event_payload["payload"]["Category"],
                        event_payload["payload"]["User"]),
                    Subject="{} - File Approved".format(event_payload["payload"]["Project"])
                )

            # On "PROJECT_DELETED":
            # - set delete marker project files in S3
            # - delete project SNS topic
            if event_payload['EventType'] == "PROJECT_DELETED":
                print(
                    'Handling PROJECT_DELETED notification for {}'.format(event_payload["payload"]["ProjectId"]))

                # delete project sns topic
                print("Deleting sns project topic")
                sns_res = sns.delete_topic(TopicArn=event_payload["payload"]["ProjectSubscriptionARN"])
                print("sns delete response", sns_res)

                # delete project file objects and versions
                bucket_name = "builder-co-prod"
                objects_to_delete = event_payload["payload"]["ObjectsToDelete"]

                print("Deleting s3 objects - ", len(objects_to_delete))

                s3_delete_res = s3.delete_objects(
                    Bucket=bucket_name,
                    Delete={
                        'Quiet': True,
                        'Objects': objects_to_delete,
                    }
                )

                print("s3 delete response", s3_delete_res)

    return {'statusCode': 200}
