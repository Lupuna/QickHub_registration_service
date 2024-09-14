from django.core.files.storage import FileSystemStorage
from django.core.files import File

from .test_base import Settings
from unittest.mock import patch, MagicMock
from user_profile.tasks import upload_file


@patch('user_profile.tasks.S3Client')
@patch('user_profile.tasks.FileSystemStorage')
class UploadFileTaskTestCase(Settings):
    def setUp(self):
        self.mock_s3 = MagicMock()
        self.mock_fs = MagicMock()
        storage = FileSystemStorage()
        storage.save('test.jpeg', File(self.image))
        self.path = storage.path('test.jpeg')

    def test_upload_file_success(self, mock_storage, mock_s3client):
        mock_s3client.return_value = self.mock_s3
        mock_storage.return_value = self.mock_fs
        upload_file(self.path)

        self.mock_s3.upload_file.assert_called_once_with(self.path)
        self.mock_fs.delete.assert_called_once_with(self.path)