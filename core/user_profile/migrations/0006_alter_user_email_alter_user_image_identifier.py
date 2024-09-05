# Generated by Django 5.0.7 on 2024-09-03 13:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0005_alter_user_image_identifier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='image_identifier',
            field=models.UUIDField(default=uuid.UUID('b9a97a00-98b5-4c6e-986e-69f4cfdba271'), editable=False, help_text='uuid for image', unique=True),
        ),
    ]
