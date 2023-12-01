from .aws import AWS


class SQS(AWS):
    service_name = 'sqs'
    queue_name = 'BuildercoProcessQueue'

    @classmethod
    def create_queue(cls, name, **attributes):
        client = SQS.get_client()

        return client.create_queue(
            QueueName=name,
            Attributes=attributes,
        )

    @classmethod
    def send_message(cls, message, queue_name=None):
        sqs_client = SQS.get_client()

        if not queue_name:
            queue_name = cls.queue_name

        response = sqs_client.get_queue_url(QueueName=queue_name)
        return sqs_client.send_message(QueueUrl=response['QueueUrl'], MessageBody=message)
