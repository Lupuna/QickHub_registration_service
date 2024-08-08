from django.urls import reverse, resolve
from .test_base import Settings
from user_profile.views import ProfileAPIVewSet


class ProfileAPIRouterTestCase(Settings):

    def test_profile_detail_route(self):
        url = reverse('user-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, ProfileAPIVewSet)
