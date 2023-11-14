from .aws import AWS


class SQS(AWS):
    service_name = 'sqs'

    @classmethod
    def create_queue(cls, name, **attributes):
        client = SQS.get_client()

        return client.create_queue(
            QueueName=name,
            Attributes=attributes,
        )
