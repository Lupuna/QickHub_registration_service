from celery import shared_task
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from core.storage_client import S3Client


@shared_task
def upload_file(path: str):
    storage = FileSystemStorage()

    try:
        client = S3Client(
            '679970d1e64c4b3f91f3c734d22115aa',
            '583424ee43e047d38be860bc83238c9e',
            settings.STORAGE_URL,
            settings.BUCKET_NAME,
        )
        client.upload_file(path)
    finally:
        storage.delete(path)


