from io import BytesIO
from PIL import Image
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase

from user_profile.models import User, Customization, Link, Reminders, Notifications


class Settings(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(
            email='admin@gmail.com',
            password='test_password',
            first_name='test_first_name',
            last_name='test_last_name',
            image_identifier='d14fd3b8-2f36-4793-87e5-ae5ac108c237',
            date_joined='2024-11-19T18:12:03.445840Z'
        )

        cls.zhumshut = User.objects.create(
            email='us@example.com',
            first_name='zhumshut',
            last_name='',
            phone='null',
            image_identifier="c3f1b16c-8102-45b7-b8b5-666f268982fc",
            date_joined='2024-11-25T04:57:29Z',
        )

        cls.link_1 = Link.objects.create(
            user=cls.user,
            title=0,
            link='https://code.djangoproject.com/wiki/IntegrityError'
        )

        cls.link_2 = Link.objects.create(
            user=cls.user,
            title=2,
            link='https://code.djangoproject.com/wiki/IntegrityError'
        )

        cls.link_3 = Link.objects.create(
            user=cls.user,
            title=1,
            link='https://code.djangoproject.com/wiki/IntegrityError'
        )

        cls.customization = Customization.objects.create(
            user=cls.user
        )

        cls.reminder = Reminders.objects.create(
            user=cls.user
        )

        cls.notification = Notifications.objects.create(
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
