from django.test import TestCase
from rest_framework.exceptions import ValidationError

from jwt_registration.serializers import UserImportantSerializer
from user_profile.models import User


class UserImportantSerializerTestCase(TestCase):

    def setUp(self):
        self.data = {
            'email': 'testuser@example.com',
            'password': 'test_pass123',
            'password2': 'test_pass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        self.wrong_data = {
            'email': 'testuser@example.com',
            'password': 'test_pass123',
            'password2': 'wrong_test_pass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        self.partial_update_data = {
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
        }

    def test_valid_data(self):
        serializer = UserImportantSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, self.data['email'])
        self.assertEqual(user.first_name, self.data['first_name'])
        self.assertEqual(user.last_name, self.data['last_name'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertNotEqual(user.password, self.data['password'])

    def test_password_mismatch(self):
        serializer = UserImportantSerializer(data=self.wrong_data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Password mismatch', str(e.exception))

    def test_create_user_missing_first_name(self):
        invalid_data = self.data.copy()
        invalid_data.pop('first_name')
        serializer = UserImportantSerializer(data=invalid_data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn('First name is required.', str(e.exception))

    def test_create_user_missing_last_name(self):
        invalid_data = self.data.copy()
        invalid_data.pop('last_name')
        serializer = UserImportantSerializer(data=invalid_data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Last name is required.', str(e.exception))

    def test_create_user(self):
        serializer = UserImportantSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(User.objects.filter(email=self.data['email']).exists())
        self.assertTrue(User.objects.get(email=self.data['email']).check_password(self.data['password']))
        self.assertEqual(user.first_name, self.data['first_name'])
        self.assertEqual(user.last_name, self.data['last_name'])

    def test_update_user(self):
        user = User.objects.create_user(
            email='olduser@example.com',
            password='newpass_123',
            first_name='Old',
            last_name='Older'
        )
        serializer = UserImportantSerializer(instance=user, data=self.data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.email, self.data['email'])
        self.assertFalse(updated_user.first_name == self.data['first_name'])
        self.assertFalse(updated_user.last_name == self.data['last_name'])
        self.assertTrue(updated_user.check_password(self.data['password']))
