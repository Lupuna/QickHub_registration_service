from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from .test_base import Settings
from user_profile.models import Link
from django.utils.translation import gettext_lazy as _


class TestUser(Settings):

    def setUp(self):
        self.valid_phone_numbers = [
            "+7 123 4567890",
            "8 123 456 7890",
            "81234567890",
            "+7-123-456-78-90",
            "8(123)456-78-90",
            "123-45-67"
        ]
        self.invalid_phone_numbers = [
            "+1 123 4567890",
            "123456",
            "+7 (123) 45",
            "+7123456789012345",
            "abcdefg"
        ]

    def test_str_method(self):
        self.assertEqual(str(self.user), self.user.get_full_name())

    def test_valid_phone_numbers(self):
        for number in self.valid_phone_numbers:
            self.user.phone = number
            try:
                self.user.full_clean()
            except ValidationError:
                self.fail(f"Valid phone number {number} raised ValidationError")

    def test_invalid_phone_numbers(self):
        for number in self.invalid_phone_numbers:
            self.user.phone = number
            with self.assertRaises(ValidationError):
                self.user.full_clean()

    def test_email_index(self):
        indexes = [index.name for index in self.user._meta.indexes]
        self.assertIn('user_email_idx', indexes)

    def test_verbose_name(self):
        self.assertEqual(self.user._meta.verbose_name, _("User"))
        self.assertEqual(self.user._meta.verbose_name_plural, _("Users"))

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), ("%s %s" % (self.user.first_name, self.user.last_name)).strip())


class TestCustomization(Settings):

    def test_str_method(self):
        correct_meaning = f'{self.customization.color_scheme} {self.customization.font_size}'
        self.assertEqual(str(self.customization), correct_meaning)

    def test_font_size_validator(self):
        self.customization.font_size = 31
        with self.assertRaises(ValidationError):
            self.customization.full_clean()

    def test_verbose_name(self):
        self.assertEqual(self.customization._meta.verbose_name, _("Customization"))
        self.assertEqual(self.customization._meta.verbose_name_plural, _("Customizations"))


class TestLink(Settings):

    def test_str_method(self):
        self.assertEqual(str(self.link_1), self.link_1.title)

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            wrong_link = Link.objects.create(
                user=self.user,
                title=self.link_1.title,
                link='https://test_duplicate_link.com/'
            )

    def test_verbose_name(self):
        self.assertEqual(self.link_1._meta.verbose_name, "Link")
        self.assertEqual(self.link_1._meta.verbose_name_plural, "Links")
