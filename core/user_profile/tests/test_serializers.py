from django.db import IntegrityError
from .test_base import Settings
from rest_framework import serializers
from user_profile.serializers import LinkSerializer, CustomizationSerializer, ProfileUserSerializer


class LinkSerializerTestCase(Settings):

    def test_link_serializer_contains_expected_fields(self):
        serializer = LinkSerializer(self.link_1)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'title', 'link'))

    def test_link_serializer_read_only_id(self):
        serializer = LinkSerializer(self.link_1, data={'id': 999, 'title': self.link_1.title, 'link': self.link_1.link})
        serializer.is_valid()
        print(serializer.errors)
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.link_1.id)
        self.assertNotEqual(updated_link.id, 999)


class CustomizationSerializerTestCase(Settings):

    def test_customization_serializer_contains_expected_fields(self):
        serializer = CustomizationSerializer(self.customization)
        data = serializer.data
        self.assertEqual(tuple(data.keys()), ('id', 'color_scheme', 'font_size'))

    def test_customization_serializer_read_only_id(self):
        serializer = CustomizationSerializer(self.customization, data={'id': 999})
        self.assertTrue(serializer.is_valid())
        updated_link = serializer.save()
        self.assertEqual(updated_link.id, self.customization.id)
        self.assertNotEqual(updated_link.id, 999)
