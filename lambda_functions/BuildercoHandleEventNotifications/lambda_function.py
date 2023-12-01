import boto3
import ast
import json

session = boto3.session.Session()

sns_client = session.client('sns')
s3_client = session.client('s3')
sqs_client = session.client('sqs')


def lambda_handler(event, context):
    print("running lambda function for records {}".format(len(event['Records'])))

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

                # On "FILE_APPROVED" or ALL_FILES_APPROVED send Project SNS notification
                if event_type == "FILE_APPROVED" or event_type == "ALL_FILES_APPROVED":
                    message = None
                    subject = None
                    file_name = payload["FileName"]
                    category = payload["Category"]
                    project_name = payload["ProjectName"]

                    if event_type == "ALL_FILES_APPROVED":
                        subject = "{} - File Status Updated".format(project_name)
                        message = 'Construction of project "{}({})" is all set to beign and project files approved. Login to Builderco to see project'.format(
                            project_name, category)

                    if event_type == "FILE_APPROVED":
                        subject = "{} - File Approved".format(project_name)
                        message = "{}({}) in {} has been approved. Login to Builderco to see approved file".format(
                            file_name, category, project_name)

                    if message and subject:
                        sns_client.publish(
                            TopicArn=payload["ProjectSubscriptionARN"],
                            Subject=subject,
                            Message=message,
                        )

    return {'statusCode': 200}
