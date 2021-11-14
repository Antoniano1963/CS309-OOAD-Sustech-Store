# Generated by Django 3.2.9 on 2021-11-12 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20211112_2224'),
        ('user', '0004_auto_20211111_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_target',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='comments_target_mer', to='user.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='comment_number_for_task',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_use_mer', to='user.user'),
        ),
        migrations.CreateModel(
            name='CommentTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_content', models.CharField(max_length=512)),
                ('comment_date', models.DateTimeField(auto_now_add=True)),
                ('comment_level', models.IntegerField(choices=[(1, '非常不满'), (2, '不满'), (3, '一般'), (4, '较为满意'), (5, '十分满意')])),
                ('agree_number', models.IntegerField(default=0)),
                ('disagree_number', models.IntegerField(default=0)),
                ('comment_target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_target_task', to='user.user')),
                ('comment_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_task', to='task.task')),
                ('comment_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_user_task', to='user.user')),
            ],
            options={
                'ordering': ['-agree_number', 'disagree_number'],
            },
        ),
    ]
