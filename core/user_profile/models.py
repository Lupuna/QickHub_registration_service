from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator
from django.db import models
import uuid


class User(AbstractUser):
    email = models.EmailField(_("email address"))
    phone = models.CharField(
        max_length=25,
        validators=[
            RegexValidator('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
        ],
        blank=True,
    )
    image_identifier = models.UUIDField(
        default=uuid.uuid4(),
        editable=False,
        unique=True,
        help_text=_('uuid for image')
    )
    city = models.CharField(max_length=255, blank=True)
    birthday = models.DateField(blank=True, null=True, )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
        ]

    def __str__(self):
        return self.email


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

    def __str__(self):
        return self.title
