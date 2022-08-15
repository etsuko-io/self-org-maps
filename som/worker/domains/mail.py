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
        # Try to send the email.
        try:
            # Provide the contents of the email.
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
                # If you are not using a configuration set, comment or delete the
                # following line
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
        else:
            logger.info(f"Email sent! Message ID: {response['MessageId']}"),


if __name__ == "__main__":
    sender = "SOM Queue <rubencronie@gmail.com>"
    recipient = "rubencronie@gmail.com"
    aws_region = "eu-west-1"
    subject = "Amazon SES Test (SDK for Python)"
    body_text = (
        "Amazon SES Test (Python)\r\n"
        "This email was sent with Amazon SES using the "
        "AWS SDK for Python (Boto)."
    )

    # The HTML body of the email.
    body_html = """<html>
    <head></head>
    <body>
      <h1>Amazon SES Test (SDK for Python)</h1>
      <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
          AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
                """

    email = Email(
        sender=sender,
        recipient=recipient,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
    )
    email.send()
