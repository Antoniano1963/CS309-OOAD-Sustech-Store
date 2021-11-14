from django.db import models

# Create your models here.


from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.


class Dialogue(models.Model):
    class DialogueType(models.IntegerChoices):
        NORMAL = (1, '常规')
        TASK = (2, '用于task')
    dialogue_user1 = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user_dialogues')
    dialogue_user2 = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='business_dialogues')
    create_date = models.DateTimeField(auto_now_add=True)
    dialogue_user1_key = models.CharField(null=True, blank=True, max_length=64)
    dialogue_user2_key = models.CharField(null=True, blank=True, max_length=64)
    update_date = models.DateTimeField(null=True)
    user1_wait_message_number = models.IntegerField(default=0)
    user2_wait_message_number = models.IntegerField(default=0)
    dialogue_type = models.IntegerField(choices=DialogueType.choices, default=1)
    #可以通过wait_number来知道那些是新发的吧
    dialogue_info = ArrayField(
        base_field=models.JSONField(),
        blank=True,
        default=list
    )
    dialogue_info_user1_wait = ArrayField(
        base_field=models.JSONField(),
        blank=True,
        default=list
    )
    dialogue_info_user2_wait = ArrayField(
        base_field=models.JSONField(),
        blank=True,
        default=list
    )
    unread_num = models.IntegerField(default=0)