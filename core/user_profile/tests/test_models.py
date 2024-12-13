from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from user_profile.models import Link, Reminders, Notifications
from .test_base import Settings


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
        self.assertEqual(str(self.link_1), str(self.link_1.title))

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


class TestReminders(Settings):

    def test_str(self):
        self.assertEqual(str(self.reminder),
                         'days_before_start_task: 1  |  exact_time_of_day_before_start_task: 8  |  time_before_deadline: 30  |  remind_about_expire_in: В начале следующей недели')

    def test_verbose_names(self):
        self.assertEqual(self.reminder._meta.verbose_name, _('Reminder'))
        self.assertEqual(self.reminder._meta.verbose_name_plural, _("Reminders"))

    def test_default_vals(self):
        self.assertEqual(self.reminder.days_before_start_task, 1)
        self.assertEqual(self.reminder.exact_time_of_day_before_start_task, 8)
        self.assertEqual(self.reminder.time_before_deadline, 30)
        self.assertEqual(self.reminder.remind_about_expire_in, 'В начале следующей недели')

    def test_relation(self):
        user = self.reminder.user
        self.assertEqual(user, self.user)


class NotificationTestCase(Settings):

    def test_str(self):
        self.assertEqual(str(self.notification),
                         'chat_message: ring=True \ browser=True  |  is_executor: ring=True \ browser=True  |  dl_expired: ring=True \ browser=True  |  task_done: ring=True \ browser=True')

    def test_verbose_names(self):
        self.assertEqual(self.notification._meta.verbose_name, _('Notification'))
        self.assertEqual(self.notification._meta.verbose_name_plural, _("Notifications"))

    def test_default_vals(self):
        self.assertEqual(self.notification.chat_message_ring, True)
        self.assertEqual(self.notification.chat_message_in_browser, True)
        self.assertEqual(self.notification.is_executor_ring, True)
        self.assertEqual(self.notification.is_executor_in_browser, True)
        self.assertEqual(self.notification.dl_expired_ring, True)
        self.assertEqual(self.notification.dl_expired_in_browser, True)
        self.assertEqual(self.notification.task_done_ring, True)
        self.assertEqual(self.notification.task_done_in_browser, True)

    def test_relation(self):
        user = self.notification.user
        self.assertEqual(user, self.user)
