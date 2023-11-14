from uuid import uuid4

from .aws import AWS


class SNS(AWS):
    service_name = 'sns'

    @classmethod
    def create_topic(cls, name, is_fifo=False, **attributes):
        client = SNS.get_client()

        topic_name = name

        if is_fifo:
            attributes["FifoTopic"] = True
            topic_name = str(name) + ".fifo"

        return client.create_topic(
            Name=topic_name,
            Attributes=attributes,
        )

    @classmethod
    def subscribe(cls, topic_arn, protocol, endpoint, return_subscription_arn=True, **attributes):
        client = SNS.get_client()

        return client.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,
            Endpoint=endpoint,
            Attributes=attributes,
            ReturnSubscriptionArn=return_subscription_arn
        )

    @classmethod
    def unsubscribe(cls, subscription_arn):
        client = SNS.get_client()

        return client.unsubscribe(
            SubscriptionArn=subscription_arn
        )

    @classmethod
    def publish(cls, topic_arn, subject, message, **message_attributes):
        client = SNS.get_client()

        return client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject,
            MessageAttributes=message_attributes,
            MessageDeduplicationId=str(uuid4()),
        )
