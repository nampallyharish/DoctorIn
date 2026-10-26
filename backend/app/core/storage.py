"""S3-compatible Object Storage abstraction for secure document and image management."""

from typing import BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


class StorageClient:
    """Interface to S3-compatible object storage (AWS S3, Cloudflare R2, MinIO)."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                use_ssl=settings.S3_USE_SSL,
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        return self._client

    def upload_file(
        self,
        file_obj: BinaryIO,
        key: str,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        """Upload file object to S3."""
        extra_args = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata

        try:
            self.client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs=extra_args,
            )
            return key
        except ClientError as e:
            logger.error(f"S3 upload error for key '{key}': {e}")
            raise

    def generate_presigned_url(
        self,
        key: str,
        expires_in_seconds: int = 3600,
        operation: str = "get_object",
    ) -> str:
        """Generate a short-lived presigned URL for private file access."""
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=operation,
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for key '{key}': {e}")
            raise

    def delete_file(self, key: str) -> bool:
        """Delete file by key from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            logger.error(f"S3 deletion error for key '{key}': {e}")
            return False


storage = StorageClient()
