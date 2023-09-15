import boto3


class S3Client:
    def __init__(self):
        """
        Store your access keys in the env variables:

        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY

        When using temporary credentials:
        - AWS_SESSION_TOKEN
        """
        self._boto3 = boto3.client("s3")

    def save(self, data: bytes, bucket: str, path: str):
        return self._boto3.put_object(Body=data, Bucket=bucket, Key=path)
