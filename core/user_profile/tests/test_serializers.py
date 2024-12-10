from unittest.mock import patch

from rest_framework.exceptions import MethodNotAllowed

from user_profile.models import Link
from user_profile.serializers import LinkSerializer, CustomizationSerializer, ProfileUserSerializer, ImageSerializer, NotificationSerializer, ReminderSerializer, DepartmentForUsersInfoSerializer, PositionForUsersInfoSerializer
from .test_base import Settings, mock_upload_file


class LinkSerializerTestCase(Settings):

    def test_link_serializer_contains_expected_fields(self):
        serializer = LinkSerializer(self.link_1)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'title', 'link'))

    def test_link_serializer_read_only_id(self):
        serializer = LinkSerializer(self.link_1, data={
                                    'id': 999, 'title': self.link_1.title, 'link': self.link_1.link})
        serializer.is_valid()
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.link_1.id)
        self.assertNotEqual(updated_link.id, 999)


class CustomizationSerializerTestCase(Settings):

    def test_customization_serializer_contains_expected_fields(self):
        serializer = CustomizationSerializer(self.customization)
        data = serializer.data
        self.assertEqual(tuple(data.keys()),
                         ('id', 'color_scheme', 'font_size'))

    def test_customization_serializer_read_only_id(self):
        serializer = CustomizationSerializer(
            self.customization, data={'id': 999})
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
            'reminder': {'days_before_start_task': 1},
            'notification': {'chat_message_ring': True},
            'links': [
                {'title': 0, 'link': 'http://updatedlink1.com'},
                {'title': 1, 'link': 'http://link3.com'},
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
                'links', 'customization', 'reminder',
                'notification', 'first_name', 'last_name',
            )
        )

    def test_profile_user_serializer_read_only(self):
        serializer = ProfileUserSerializer(
            self.user, data={'id': 999, 'email': 'wrong_email@gmail.com'})
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
        self.assertEqual(e.exception.detail,
                         'Creation is not allowed using this serializer.')
        self.assertEqual(e.exception.status_code, 405)

    def test_update_method(self):
        serializer = ProfileUserSerializer(
            instance=self.user, data=self.validated_data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.phone, self.validated_data['phone'])
        self.assertEqual(updated_user.city, self.validated_data['city'])
        self.assertEqual(str(updated_user.birthday),
                         self.validated_data['birthday'])

        self.assertEqual(updated_user.phone, self.validated_data['phone'])
        self.assertEqual(updated_user.city, self.validated_data['city'])
        self.assertEqual(str(updated_user.birthday),
                         self.validated_data['birthday'])
        self.assertEqual(updated_user.first_name,
                         self.validated_data['first_name'])
        self.assertEqual(updated_user.last_name,
                         self.validated_data['last_name'])

        updated_customization = updated_user.customization
        self.assertEqual(updated_customization.font_size,
                         self.validated_data['customization']['font_size'])

        self.assertTrue(Link.objects.filter(
            user=self.user, title=0).exists())

        updated_reminder = updated_user.reminder
        self.assertEqual(updated_reminder.days_before_start_task,
                         self.validated_data['reminder']['days_before_start_task'])

        updated_note = updated_user.notification
        self.assertEqual(updated_note.chat_message_ring,
                         self.validated_data['notification']['chat_message_ring'])

    def test_update_method_with_no_links_and_customisation(self):
        data_without_links = {
            'phone': '0987654321',
            'city': 'Another City',
            'birthday': '1992-02-02'
        }
        serializer = ProfileUserSerializer(
            instance=self.user, data=data_without_links)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.phone, data_without_links['phone'])
        self.assertEqual(updated_user.city, data_without_links['city'])
        self.assertEqual(str(updated_user.birthday),
                         data_without_links['birthday'])

        updated_customization = updated_user.customization
        self.assertEqual(updated_customization.font_size, 15)
        self.assertEqual(Link.objects.filter(user=self.user).count(), 3)


@patch('user_profile.serializers.upload_file', side_effect=mock_upload_file)
class ImageSerializerTestCase(Settings):

    def test_serializer_valid_data(self, mock_upload_file):
        data = {'user': self.user.id, 'image': self.image}
        serializer = ImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        result = serializer.save()
        self.assertEqual(result['status'], True)

    def test_serializer_invalid_image(self, mock_upload_file):
        data = {'user': self.user.id}
        serializer = ImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)


class NotificationsSerializerTestCase(Settings):

    def test_notification_serializer_contains_expected_fields(self):
        serializer = NotificationSerializer(self.notification)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'chat_message_ring', 'chat_message_in_browser', 'is_executor_ring',
                         'is_executor_in_browser', 'dl_expired_ring', 'dl_expired_in_browser', 'task_done_ring', 'task_done_in_browser'))

    def test_notifications_serializer_read_only_id(self):
        serializer = NotificationSerializer(
            self.notification, data={'id': 999})
        self.assertTrue(serializer.is_valid())
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.notification.id)
        self.assertNotEqual(updated_link.id, 999)


class RemindersSerializerTestCase(Settings):

    def test_reminder_serializer_contains_expected_fields(self):
        serializer = ReminderSerializer(self.reminder)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'days_before_start_task',
                         'exact_time_of_day_before_start_task', 'time_before_deadline', 'remind_about_expire_in'))

    def test_reminder_serializer_read_only_id(self):
        serializer = NotificationSerializer(self.reminder, data={'id': 999})
        self.assertTrue(serializer.is_valid())
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.reminder.id)
        self.assertNotEqual(updated_link.id, 999)


class DepartmentForUserSerTestCase(Settings):

    def test_dep_serializer_contains_expected_fields(self):
        serializer = DepartmentForUsersInfoSerializer()
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'title',
                         'description', 'parent', 'company', 'color'))


class PositionsForUserSerTestCase(Settings):

    def test_dep_serializer_contains_expected_fields(self):
        serializer = PositionForUsersInfoSerializer()
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'title',
                                              'description', 'access_weight', 'company'))
