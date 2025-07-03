import boto3
from functools import lru_cache

from app.config import Settings

settings = Settings()

class AwsService:
    def __init__(self, region_name: str = settings.AWS_DEFAULT_REGION):
        self.region_name = region_name
        self._clients = {}

    def get_client(self, service_name: str):
        if service_name not in self._clients:
            if settings.ENVIRONMENT == "local":
                self._clients[service_name] = boto3.resource(
                    service_name,
                    region_name=settings.AWS_DEFAULT_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            else:
                self._clients[service_name] = boto3.resource(
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

@lru_cache()
def get_aws_service() -> AwsService:
    return AwsService()
