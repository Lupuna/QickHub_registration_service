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

        self.data_without_password2 = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
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

    def test_missing_password2(self):
        serializer = UserSerializer(data=self.data_without_password2)
        self.assertTrue(serializer.is_valid())

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
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass_123',
        }
        serializer = UserSerializer(instance=user, data=data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, 'newuser')
        self.assertEqual(updated_user.email, 'newuser@example.com')
        self.assertTrue(updated_user.check_password('newpass_123'))

    def test_update_user_with_password2(self):
        user = User.objects.create_user(username='olduser2', email='olduser2@example.com', password='oldpass2_123')
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'newpass2_123',
            'password2': 'newpass2_123'
        }
        serializer = UserSerializer(instance=user, data=data)
        self.assertTrue(serializer.is_valid())
