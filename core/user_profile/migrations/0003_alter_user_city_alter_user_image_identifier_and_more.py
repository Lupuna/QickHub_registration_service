# Generated by Django 5.0.7 on 2024-08-08 07:09

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_remove_user_image_user_image_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.UUID('c50ca990-6c37-42b3-9cec-726b14fd0d49'), editable=False, help_text='uuid for image', unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=25, null=True, validators=[django.core.validators.RegexValidator('^((8|\\+7)[\\- ]?)?(\\(?\\d{3}\\)?[\\- ]?)?[\\d\\- ]{7,10}$')]),
        ),
    ]
