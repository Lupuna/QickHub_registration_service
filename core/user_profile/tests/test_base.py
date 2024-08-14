from django.test import TestCase
from user_profile.models import User, Customization, Link


class Settings(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_user_1',
            email='test_email@gmail.com',
            password='test_password',
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