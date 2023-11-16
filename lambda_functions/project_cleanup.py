import boto3


def lambda_handler(event, context):
    client = boto3.client('sns')

    snsArn = 'arn:aws:sns:Region:AccountID:TestTopic'

    message = "This is a test notification."

    response = client.publish(
        TopicArn=snsArn,
        Message=message,
        Subject='Hello'
    )

    return True  ## project and file infofrmation
