# Generated by Django 3.2.9 on 2021-11-08 02:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='favorite_merchandise',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=128),
        ),
        migrations.AlterField(
            model_name='user',
            name='favorite_sellers',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=128),
        ),
        migrations.AlterField(
            model_name='user',
            name='notice_info',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='user',
            name='notice_info_unread',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_recommend_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_transactions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None),
        ),
    ]
