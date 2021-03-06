# Generated by Django 3.2.9 on 2021-11-11 00:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
        ('user', '0003_auto_20211109_0017'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stars_for_task',
            field=models.IntegerField(default=5),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_content', models.CharField(max_length=512)),
                ('comment_date', models.DateTimeField(auto_now_add=True)),
                ('comment_level_mer', models.IntegerField(choices=[(1, '非常不满'), (2, '不满'), (3, '一般'), (4, '较为满意'), (5, '十分满意')])),
                ('comment_level_attitude', models.IntegerField(choices=[(1, '非常不满'), (2, '不满'), (3, '一般'), (4, '较为满意'), (5, '十分满意')])),
                ('comment_level_tra', models.IntegerField(choices=[(1, '非常不满'), (2, '不满'), (3, '一般'), (4, '较为满意'), (5, '十分满意')])),
                ('agree_number', models.IntegerField(default=0)),
                ('disagree_number', models.IntegerField(default=0)),
                ('comment_transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_tra', to='order.transaction')),
                ('comment_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_user', to='user.user')),
            ],
            options={
                'ordering': ['-agree_number', 'disagree_number'],
            },
        ),
    ]
