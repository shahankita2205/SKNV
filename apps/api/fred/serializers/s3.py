"""
S3 Service
"""

import logging
import subprocess

from django.conf import settings

logger = logging.getLogger(__name__)


class S3ErrorCodes:
    ERROR_UPLOAD_FAILED = 24001
    ERROR_DOWNLOAD_FAILED = 24002
    ERROR_FILE_NOT_FOUND = 24003


class S3ServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class S3Service:

    def __init__(self):
        try:
            import boto3

            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
                region_name=getattr(settings, "AWS_REGION", "us-east-1"),
            )
            self.bucket = getattr(settings, "AWS_BUCKET", None)
        except ImportError:
            logger.warning("boto3 not installed, S3 operations will not work")
            self.s3_client = None
            self.bucket = None

    def upload(self, file_path: str, s3_path: str) -> bool:
        if not self.s3_client:
            raise S3ServiceException(
                "S3 client not initialized", S3ErrorCodes.ERROR_UPLOAD_FAILED
            )

        try:
            with open(file_path, "rb") as f:
                self.s3_client.upload_fileobj(f, self.bucket, s3_path)
            logger.info(f"Uploaded {file_path} to s3://{self.bucket}/{s3_path}")
            return True
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise S3ServiceException(
                f"Upload failed: {str(e)}", S3ErrorCodes.ERROR_UPLOAD_FAILED
            )

    def generate_url(self, file_key: str, expires_in: int = 1200) -> str:
        if not self.s3_client:
            raise S3ServiceException(
                "S3 client not initialized", S3ErrorCodes.ERROR_DOWNLOAD_FAILED
            )

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": file_key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise S3ServiceException(
                f"Failed to generate URL: {str(e)}", S3ErrorCodes.ERROR_DOWNLOAD_FAILED
            )

    def zip_and_upload(self, files_path: str, zip_path: str, s3_path: str) -> bool:
        try:
            result = subprocess.run(
                ["zip", "-j", zip_path, files_path], capture_output=True, text=True
            )
            if result.returncode != 0:
                raise S3ServiceException(
                    f"Zip failed: {result.stderr}", S3ErrorCodes.ERROR_UPLOAD_FAILED
                )
            return self.upload(zip_path, s3_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Zip and upload failed: {e}")
            raise S3ServiceException(
                f"Zip and upload failed: {str(e)}", S3ErrorCodes.ERROR_UPLOAD_FAILED
            )

    def download(self, s3_path: str, local_path: str) -> bool:
        if not self.s3_client:
            raise S3ServiceException(
                "S3 client not initialized", S3ErrorCodes.ERROR_DOWNLOAD_FAILED
            )

        try:
            self.s3_client.download_file(self.bucket, s3_path, local_path)
            logger.info(f"Downloaded s3://{self.bucket}/{s3_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            raise S3ServiceException(
                f"Download failed: {str(e)}", S3ErrorCodes.ERROR_DOWNLOAD_FAILED
            )

    def file_exists(self, s3_path: str) -> bool:
        if not self.s3_client:
            return False
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_path)
            return True
        except:
            return False


_s3_service = None


def get_s3_service() -> S3Service:
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service


__all__ = [
    "S3ErrorCodes",
    "S3ServiceException",
    "S3Service",
    "get_s3_service",
]
