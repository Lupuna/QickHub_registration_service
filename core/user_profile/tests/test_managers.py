from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTestCase(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.valid_email = 'test_user@gmial.com'
        self.valid_password = 'test_password_123'

    def test_create_user_with_email_success(self):
        user = self.user_model.objects.create_user(
            email=self.valid_email,
            password=self.valid_password
        )
        self.assertEqual(user.email, self.valid_email)
        self.assertTrue(user.check_password(self.valid_password))

    def tset_create_user_no_email_raises_error(self):
        with self.assertRaises(ValueError):
            self.user_model.objects.create_user(email=None, password=self.valid_password)

    def test_create_superuser(self):
        user = self.user_model.objects.create_superuser(
            email=self.valid_email,
            password=self.valid_password
        )
        self.assertEqual(user.email, self.valid_email)
        self.assertTrue(user.check_password(self.valid_password))
        self.assertTrue(user.is_staff)




