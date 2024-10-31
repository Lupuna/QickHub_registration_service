# Generated by Django 5.0.7 on 2024-10-31 03:10

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0013_alter_user_image_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.UUID('729299e8-c567-440c-936e-1ce2e200fa65'), editable=False, help_text='uuid for image', unique=True),
        ),
    ]
