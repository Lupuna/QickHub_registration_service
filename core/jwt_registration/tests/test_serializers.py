from django.test import TestCase
from rest_framework.exceptions import ValidationError

from jwt_registration.serializers import RegistrationSerializer, SetNewPasswordSerializer, EmailVerifySerializer
from user_profile.models import User


class RegistrationSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {
            'email': 'test_email@gmail.com',
            'password': 'test_password',
            'password2': 'test_password',
            'first_name': 'test_name',
            'last_name': 'test_lastname'
        }

    def test_validation(self):
        serializer = RegistrationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(RegistrationSerializer.Meta.fields,
                         tuple(serializer.validated_data.keys()))

        data = self.data
        data.update({'email': 'sfsadf'})
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'password': ''})
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'password2': ''})
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'password': 'sfsadf', 'password2': 'dgcd'})
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'first_name': ''})
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'last_name': ''})
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        self.assertEqual(RegistrationSerializer.Meta.model, User)

    def test_create_user(self):
        serializer = RegistrationSerializer(data=self.data)
        if serializer.is_valid():
            user = serializer.save()
            self.assertTrue(User.objects.filter(email=user.email).exists())


class EmailVerifySerializerTestCase(TestCase):
    def setUp(self):
        self.data = {
            'email': 'test_email@gmail.com',
            'password': 'test_password',
            'password2': 'test_password',
        }
        self.user = User(email='test_email@gmail.com',
                         first_name='test_name', last_name='test_lastname')
        self.user.set_password('test_password')
        self.user.email_verified = False
        self.user.save()

    def test_validation(self):
        serializer = EmailVerifySerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        data = self.data
        data.update({'email': 'dgfgd'})
        serializer = EmailVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'password': 'dgfgd'})
        serializer = EmailVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())

        data = self.data
        data.update({'password': ''})
        serializer = EmailVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())

        self.user.delete()
        serializer = EmailVerifySerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
