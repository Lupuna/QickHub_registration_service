from io import BytesIO
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import MethodNotAllowed

from user_profile.models import Link
from user_profile.serializers import LinkSerializer, CustomizationSerializer, ProfileUserSerializer, ImageSerializer
from .test_base import Settings


def mock_upload_file(path: str):
    pass


class LinkSerializerTestCase(Settings):

    def test_link_serializer_contains_expected_fields(self):
        serializer = LinkSerializer(self.link_1)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'title', 'link'))

    def test_link_serializer_read_only_id(self):
        serializer = LinkSerializer(self.link_1, data={'id': 999, 'title': self.link_1.title, 'link': self.link_1.link})
        serializer.is_valid()
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.link_1.id)
        self.assertNotEqual(updated_link.id, 999)


class CustomizationSerializerTestCase(Settings):

    def test_customization_serializer_contains_expected_fields(self):
        serializer = CustomizationSerializer(self.customization)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'color_scheme', 'font_size'))

    def test_customization_serializer_read_only_id(self):
        serializer = CustomizationSerializer(self.customization, data={'id': 999})
        self.assertTrue(serializer.is_valid())
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.customization.id)
        self.assertNotEqual(updated_link.id, 999)


class ProfileUserSerializerTestCase(Settings):

    def setUp(self):
        self.validated_data = {
            'phone': '0987654321',
            'city': 'New City',
            'birthday': '1995-01-01',
            'first_name': 'new_first_name',
            'last_name': 'new_last_name',
            'customization': {'font_size': 15},
            'links': [
                {'title': 'Link 1', 'link': 'http://updatedlink1.com'},
                {'title': 'Link 3', 'link': 'http://link3.com'},
            ]
        }

    def test_profile_user_serializer_contains_expected_fields(self):
        serializer = ProfileUserSerializer(self.user)
        data = serializer.data
        self.assertEqual(
            tuple(data.keys()),
            (
                'id', 'image_identifier',
                'phone', 'city', 'birthday',
                'links', 'customization', 'first_name', 'last_name'
            )
        )

    def test_profile_user_serializer_read_only(self):
        serializer = ProfileUserSerializer(self.user, data={'id': 999, 'email': 'wrong_email@gmail.com'})
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        with self.subTest('check id'):
            self.assertEqual(updated_user.id, self.user.id)
            self.assertNotEqual(updated_user.id, 999)
        with self.subTest('check email'):
            self.assertEqual(updated_user.email, self.user.email)
            self.assertNotEqual(updated_user.email, 'wrong_email@gmail.com')

    def test_create_method(self):
        serializer = ProfileUserSerializer()
        with self.assertRaises(MethodNotAllowed) as e:
            serializer.create(self.validated_data)
        self.assertEqual(e.exception.detail, 'Creation is not allowed using this serializer.')
        self.assertEqual(e.exception.status_code, 405)

    def test_update_method(self):
        serializer = ProfileUserSerializer(instance=self.user, data=self.validated_data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.phone, self.validated_data['phone'])
        self.assertEqual(updated_user.city, self.validated_data['city'])
        self.assertEqual(str(updated_user.birthday), self.validated_data['birthday'])

        self.assertEqual(updated_user.phone, self.validated_data['phone'])
        self.assertEqual(updated_user.city, self.validated_data['city'])
        self.assertEqual(str(updated_user.birthday), self.validated_data['birthday'])
        self.assertEqual(updated_user.first_name, self.validated_data['first_name'])
        self.assertEqual(updated_user.last_name, self.validated_data['last_name'])

        updated_customization = updated_user.customization
        self.assertEqual(updated_customization.font_size, self.validated_data['customization']['font_size'])

        self.assertTrue(Link.objects.filter(user=self.user, title='Link 3').exists())

    def test_update_method_with_no_links_and_customisation(self):
        data_without_links = {
            'phone': '0987654321',
            'city': 'Another City',
            'birthday': '1992-02-02'
        }
        serializer = ProfileUserSerializer(instance=self.user, data=data_without_links)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.phone, data_without_links['phone'])
        self.assertEqual(updated_user.city, data_without_links['city'])
        self.assertEqual(str(updated_user.birthday), data_without_links['birthday'])

        updated_customization = updated_user.customization
        self.assertEqual(updated_customization.font_size, 15)
        self.assertEqual(Link.objects.filter(user=self.user).count(), 3)


@patch('user_profile.serializers.upload_file', side_effect=mock_upload_file)
class ImageSerializerTestCase(Settings):

    def test_serializer_valid_data(self, mock_upload_file):
        image = self.create_test_image()
        data = {'user': self.user.id, 'image': image}
        serializer = ImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        result = serializer.save()
        self.assertEqual(result['status'], True)

    def test_serializer_invalid_image(self, mock_upload_file):
        data = {'user': self.user.id}
        serializer = ImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)

    @staticmethod
    def create_test_image():
        file = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(file, 'JPEG')
        file.name = 'test.jpeg'
        file.seek(0)
        return SimpleUploadedFile('test.jpeg', file.getvalue(), content_type='image/jpeg')
