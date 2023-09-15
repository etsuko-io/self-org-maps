import boto3
from botocore.exceptions import ClientError
from loguru import logger


class Email:
    def __init__(
        self,
        sender,
        recipient,
        subject,
        body_text,
        body_html,
        charset="UTF-8",
        region="eu-west-1",
    ):
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.body_text = body_text
        self.body_html = body_html
        self.charset = charset
        self.region = region
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = boto3.client("ses", region_name=self.region)
        return self._client

    def send(self):
        try:
            response = self.client.send_email(
                Destination={
                    "ToAddresses": [
                        self.recipient,
                    ],
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": self.charset,
                            "Data": self.body_html,
                        },
                        "Text": {
                            "Charset": self.charset,
                            "Data": self.body_text,
                        },
                    },
                    "Subject": {
                        "Charset": self.charset,
                        "Data": self.subject,
                    },
                },
                Source=self.sender,
            )
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
        else:
            logger.info(f"Email sent! Message ID: {response['MessageId']}"),
