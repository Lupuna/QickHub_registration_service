from django.urls import reverse, resolve
from .test_base import Settings
from user_profile.views import ProfileAPIVewSet, ImageAPIView


class ProfileAPIRouterTestCase(Settings):

    def test_profile_detail_route(self):
        url = reverse('user-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, ProfileAPIVewSet)

    def test_update_important_data_url_is_resolve(self):
        url = reverse('load_image')
        self.assertEqual(resolve(url).func.view_class, ImageAPIView)
