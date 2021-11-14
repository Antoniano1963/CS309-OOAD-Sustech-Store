# Generated by Django 3.2.9 on 2021-11-12 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20211111_0012'),
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_status',
            field=models.IntegerField(choices=[(0, '已取消'), (1, '等待取货'), (2, '等待送达'), (3, '等待确认'), (4, '等待评论'), (5, '已完成'), (6, '有争议'), (7, '等待送货人')], default=7),
        ),
        migrations.AlterField(
            model_name='task',
            name='upload_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks_user_upload', to='user.user'),
        ),
    ]