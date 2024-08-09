from django.test import TestCase
from rest_framework.exceptions import ValidationError
from jwt_registration.serializers import UserSerializer
from user_profile.models import User


class UserSerializerTestCase(TestCase):

    def setUp(self):
        self.data = {
            'username': 'test_user',
            'email': 'testuser@example.com',
            'password': 'test_pass123',
            'password2': 'test_pass123',
        }

        self.wrong_data = {
            'username': 'test_user',
            'email': 'testuser@example.com',
            'password': 'test_pass123',
            'password2': 'wrong_test_pass123',
        }

    def test_valid_data(self):
        serializer = UserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.data['username'])
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password(self.data['password']))
        self.assertNotEqual(user.password, self.data['password'])

    def test_password_mismatch(self):
        serializer = UserSerializer(data=self.wrong_data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Password mismatch', str(e.exception))

    def test_create_user(self):
        serializer = UserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(User.objects.filter(username=self.data['username']).exists())
        self.assertTrue(User.objects.get(username=self.data['username']).check_password(self.data['password']))

    def test_update_user(self):
        user = User.objects.create_user(
            username='olduser',
            email='olduser@example.com',
            password='newpass_123'
        )
        serializer = UserSerializer(instance=user, data=self.data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, self.data['username'])
        self.assertEqual(updated_user.email, self.data['email'])
        self.assertTrue(updated_user.check_password(self.data['password']))
