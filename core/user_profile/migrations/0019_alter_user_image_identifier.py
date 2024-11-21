# Generated by Django 5.0.7 on 2024-11-17 10:22

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0018_alter_user_image_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='uuid for image', unique=True),
        ),
    ]
