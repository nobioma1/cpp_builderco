import boto3
import ast
import json

session = boto3.session.Session()

sns_client = session.client('sns')
s3_client = session.client('s3')
sqs_client = session.client('sqs')


def lambda_handler(event, context):
    print("running lambda function - ", len(event['Records']))

    for record in event['Records']:
        if "Sns" in record:
            print("Evaluating SNS message")
            message = ast.literal_eval(record['Sns']['Message'])

            if "EventType" in message:
                event_type = message['EventType']
                payload = message["Payload"]

                print('Publishing Notification for "{}"'.format(event_type))

                # On "NEW_VERSION_UPLOAD" send Project SNS notification
                if event_type == "NEW_VERSION_UPLOAD":
                    project_name = payload["ProjectName"]
                    sns_client.publish(
                        TopicArn=payload["ProjectSubscriptionARN"],
                        Subject="{} - New File Version Uploaded".format(project_name),
                        Message="A new file version({} - v{}) has been uploaded for {} by {}. Login to Builderco to view file in project {}.".format(
                            payload["FileName"],
                            payload["VersionNumber"],
                            payload["Category"],
                            payload["User"],
                            project_name),
                    )
                    # Add new upload to into processor queue
                    response = sqs_client.get_queue_url(QueueName="BuildercoProcessQueue")
                    message_body = {
                        "EventType": "PROCESS_FILE_WATERMARK",
                        "Payload": {
                            "VersionId": payload["VersionId"],
                            "ObjectKey": payload["ObjectKey"],
                            "WatermarkText": project_name
                        }
                    }
                    queue_res = sqs_client.send_message(QueueUrl=response['QueueUrl'],
                                                        MessageBody=json.dumps(message_body))
                    print("Event {} sent into queue - {}".format(message_body["EventType"], queue_res))

                # On "FILE_APPROVED" send Project SNS notification
                if event_type == "FILE_APPROVED":
                    s3_client.publish(
                        TopicArn=payload["ProjectSubscriptionARN"],
                        Subject="{} - File Approved".format(payload["ProjectName"]),
                        Message="{}({}) has been approved by {}.".format(
                            payload["FileName"],
                            payload["Category"],
                            payload["User"]),
                    )

    return {'statusCode': 200}
