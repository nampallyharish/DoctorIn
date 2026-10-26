"""Secure File Upload and Presigned URL Service for verification documents and images."""

import uuid
from typing import BinaryIO

from app.config import get_settings
from app.core.exceptions import ValidationError
from app.core.logging import logger
from app.core.storage import storage

settings = get_settings()

ALLOWED_DOCUMENT_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class FileService:
    """Handles secure file uploads, MIME type whitelisting, and signed download URLs."""

    @staticmethod
    def validate_file_metadata(
        filename: str,
        content_type: str,
        size_bytes: int | None = None,
    ) -> str:
        """
        Validate file extension and MIME type against whitelist.
        Returns the sanitized file extension.
        """
        if content_type not in ALLOWED_DOCUMENT_MIME_TYPES:
            raise ValidationError(
                f"Unsupported file type '{content_type}'. Allowed types: PDF, JPEG, PNG."
            )

        if size_bytes and size_bytes > MAX_DOCUMENT_SIZE_BYTES:
            max_mb = MAX_DOCUMENT_SIZE_BYTES // (1024 * 1024)
            raise ValidationError(f"File size exceeds maximum permitted limit of {max_mb} MB.")

        return ALLOWED_DOCUMENT_MIME_TYPES[content_type]

    @staticmethod
    def generate_secure_storage_key(
        entity_id: uuid.UUID,
        category: str,
        file_extension: str,
    ) -> str:
        """
        Generate unguessable UUID-based S3 storage key to prevent directory traversal and file collisions.
        Example: documents/verification/123e4567-e89b-12d3-a456-426614174000/a9b8c7d6.pdf
        """
        unique_file_id = uuid.uuid4().hex
        return f"documents/{category}/{entity_id!s}/{unique_file_id}{file_extension}"

    @staticmethod
    def upload_document(
        file_obj: BinaryIO,
        entity_id: uuid.UUID | None = None,
        filename: str = "document.pdf",
        content_type: str = "application/pdf",
        size_bytes: int = 0,
        doctor_id: uuid.UUID | None = None,
        category: str = "verification",
    ) -> tuple[str, str]:
        """
        Validate and upload document to private S3 storage.
        Returns (storage_key, filename).
        """
        target_id = entity_id or doctor_id or uuid.uuid4()
        ext = FileService.validate_file_metadata(filename, content_type, size_bytes)
        storage_key = FileService.generate_secure_storage_key(target_id, category, ext)

        storage.upload_file(
            file_obj=file_obj,
            key=storage_key,
            content_type=content_type,
            metadata={"entity_id": str(target_id), "original_name": filename},
        )

        logger.info(f"Secure document uploaded for entity {target_id} with key {storage_key}")
        return storage_key, filename

    @staticmethod
    def get_presigned_download_url(storage_key: str, expires_in_seconds: int = 900) -> str:
        """
        Generate temporary presigned download URL for authorized users (15 min default TTL).
        Raw S3 paths are never exposed publicly.
        """
        return storage.generate_presigned_url(
            key=storage_key,
            expires_in_seconds=expires_in_seconds,
            operation="get_object",
        )
