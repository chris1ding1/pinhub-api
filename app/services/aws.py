import boto3
from functools import lru_cache
from botocore.exceptions import ClientError as AwsClientError

from app.config import Settings

settings = Settings()

class AwsService:
    def __init__(self, region_name: str = settings.AWS_DEFAULT_REGION):
        self.region_name = region_name
        self._clients = {}

    def get_client(self, service_name: str):
        if service_name not in self._clients:
            if service_name in ['transcribe']:
                boto3_method = boto3.client
            else:
                boto3_method = boto3.resource

            if settings.ENVIRONMENT == "local":
                self._clients[service_name] = boto3_method(
                    service_name,
                    region_name=settings.AWS_DEFAULT_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            else:
                self._clients[service_name] = boto3_method(
                    service_name,
                    region_name=settings.AWS_DEFAULT_REGION,
                )
        return self._clients[service_name]

    def get_dynamodb(self):
        return self.get_client("dynamodb")

    def get_s3(self):
        return self.get_client("s3")

    def get_ses(self):
        return self.get_client("ses")

    def get_transcribe(self):
        return self.get_client("transcribe")

    def get_s3_head_object(self, bucket_name: str, object_key: str):
        s3Client = self.get_s3()
        try:
            s3Client.meta.client.head_object(Bucket=bucket_name, Key=object_key)
            return True
        except AwsClientError as e:
            raise e

@lru_cache()
def get_aws_service() -> AwsService:
    return AwsService()
