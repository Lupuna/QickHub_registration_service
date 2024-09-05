from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from user_profile.managers import UserManager
import uuid


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email filed'), unique=True, blank=False)
    phone = models.CharField(
        max_length=25,
        validators=[
            RegexValidator(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
        ],
        blank=True,
        null=True,
    )
    image_identifier = models.UUIDField(
        default=uuid.uuid4(),
        editable=False,
        unique=True,
        help_text=_('uuid for image')
    )
    city = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Customization(models.Model):
    class ColorSchemeChoices(models.IntegerChoices):
        STANDARD = 0, _('Standard')

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customization',
        help_text=_('connection with User ')
    )
    color_scheme = models.PositiveSmallIntegerField(
        choices=ColorSchemeChoices.choices,
        default=ColorSchemeChoices.STANDARD,
        help_text=_('Color scheme for web app')
    )
    font_size = models.PositiveSmallIntegerField(default=18, validators=[
        MaxValueValidator(30)
    ])

    class Meta:
        verbose_name = _("Customization")
        verbose_name_plural = _("Customizations")

    def __str__(self):
        return f'{self.color_scheme} {self.font_size}'


class Link(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='links',
        help_text=_('connection with User ')
    )
    title = models.CharField(max_length=255, verbose_name=_('url name'))
    link = models.URLField()

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")
        unique_together = ["user", "title"]

    def __str__(self):
        return self.title
