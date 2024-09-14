from io import BytesIO
from PIL import Image
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase

from user_profile.models import User, Customization, Link


class Settings(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(
            email='test_email@gmail.com',
            password='test_password',
            first_name='test_first_name_1',
            last_name='test_last_name_!'
        )

        cls.link_1 = Link.objects.create(
            user=cls.user,
            title='test_link_1',
            link='https://code.djangoproject.com/wiki/IntegrityError'
        )

        cls.link_2 = Link.objects.create(
            user=cls.user,
            title='test_link_2',
            link='https://code.djangoproject.com/wiki/IntegrityError'
        )

        cls.link_3 = Link.objects.create(
            user=cls.user,
            title='test_link_3',
            link='https://code.djangoproject.com/wiki/IntegrityError'
        )

        cls.customization = Customization.objects.create(
            user=cls.user
        )

        cls.image = cls.create_test_image()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    @staticmethod
    def create_test_image():
        file = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file, 'JPEG')
        file.name = 'test.jpeg'
        file.seek(0)
        return SimpleUploadedFile('test.jpeg', file.getvalue(), content_type='image/jpeg')


def mock_upload_file(path: str):
    pass