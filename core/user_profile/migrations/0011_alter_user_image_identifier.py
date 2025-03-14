# Generated by Django 5.0.7 on 2024-10-05 16:23

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0010_alter_user_managers_alter_user_image_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.UUID('b3579771-1cdf-4206-84bb-73748d948dfe'), editable=False, help_text='uuid for image', unique=True),
        ),
    ]
