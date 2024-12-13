from celery import shared_task
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from core.storage_client import S3Client


@shared_task
def upload_file(path: str):
    storage = FileSystemStorage()

    try:
        client = S3Client(
            settings.STORAGE_ACCESS_KEY,
            settings.STORAGE_SECRET_KEY,
            settings.STORAGE_URL,
            settings.BUCKET_NAME,
        )
        client.upload_file(path)
    finally:
        storage.delete(path)
