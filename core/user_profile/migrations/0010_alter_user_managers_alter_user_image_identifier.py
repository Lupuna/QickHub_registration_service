# Generated by Django 5.0.7 on 2024-10-01 14:32

import user_profile.managers
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0009_remove_user_username_alter_user_image_identifier'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', user_profile.managers.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.UUID('e94637c8-442e-4853-bb23-7e9728d4c3a8'), editable=False, help_text='uuid for image', unique=True),
        ),
    ]
