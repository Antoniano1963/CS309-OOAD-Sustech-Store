# Generated by Django 3.2.9 on 2021-11-13 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20211112_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_header_photo',
            field=models.BooleanField(default=False),
        ),
    ]
