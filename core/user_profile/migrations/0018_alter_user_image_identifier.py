# Generated by Django 5.0.7 on 2024-11-14 06:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0017_alter_user_image_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.UUID('ac01c5cf-a5d9-4e62-81ca-c2e292d7d321'), editable=False, help_text='uuid for image', unique=True),
        ),
    ]
