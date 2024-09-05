from django.test import TestCase
from user_profile.models import User, Customization, Link


class Settings(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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