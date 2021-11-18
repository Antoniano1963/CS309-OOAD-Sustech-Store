from django.core.signing import TimestampSigner
from django.db import models
import django.utils.timezone
import user.models

# Create your models here.


class TaskManager(models.Manager):
    def get_tasks_by_class(self, task_type=None, sort='default'):
        '''根据商品类型id查询商品信息'''
        if sort == 'new':
            order_by = ('-upload_date',)
        elif sort == 'price':
            order_by = ('price',)
        else:
            order_by = ('-pk',)  # 按照primary key降序排列。

        # 查询数据
        if task_type:
            task_Li = self.filter(task_status__exact=7).filter(task_type__exact=task_type).order_by(*order_by)
        else:
            task_Li = self.filter(task_status__exact=7).order_by(*order_by)
        return task_Li


class Task(models.Model):

    def user_directory_path(instance, filename):
        return 'user_{0}\\user_{1}_mer\\upload_merchandise_[2]_time:_{3}_{4}'.format(instance.upload_user.id,
                                                                                     instance.upload_user.id,
                                                                                     instance.id,
                                                                                     django.utils.timezone.now(),
                                                                                     filename)

    def user_thumb_directory_path(instance, filename):
        return 'user_{0}\\user_{1}_thumb\\upload_merchandise_[2]_time:_{3}_{4}'.format(instance.upload_user.id,
                                                                                       instance.upload_user.id,
                                                                                       instance.id,
                                                                                       django.utils.timezone.now(),
                                                                                       filename)

    class TaskType(models.IntegerChoices):
        TASK1 = (1, '商品送货')
        TASK2 = (2, '外卖或快递')

    class TaskStatus(models.IntegerChoices):
        CANCEL = (0, '已取消')
        WAITDELIVER = (1, '等待取货')
        WAITRECEIVING = (2, '等待送达')
        WAITCOMFIRM = (3, '等待确认')
        WAITCOMMENT = (4, '等待评论')
        FINSIH = (5, '已完成')
        DISPUTE = (6, '有争议')
        WAITSENDER = (7, '等待送货人')

    name = models.CharField(max_length=128)
    upload_user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="tasks_user_upload")
    upload_date = models.DateTimeField(auto_now_add=True)
    task_type = models.IntegerField(choices=TaskType.choices, default=1)
    relation_transaction = models.ForeignKey('order.Transaction', on_delete=models.CASCADE,
                                             related_name="transaction_task", null=True)
    description = models.TextField(null=True)
    sender_user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='user_send_task', null=True)
    ddl_time = models.DateTimeField(null=True)
    receive_time = models.DateTimeField(null=True)
    price = models.FloatField()
    sender_addr = models.ForeignKey('user.Address', on_delete=models.CASCADE, related_name="addr_mer_10")
    receive_user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='user_receive_task', null=True)
    receive_addr = models.ForeignKey('user.Address', on_delete=models.CASCADE, related_name="addr_mer_20")
    dialogue_between_up_sender = models.ForeignKey('dialogue.Dialogue', on_delete=models.SET_NULL, null=True, related_name='dialogue_task_up')
    dialogue_between_re_sender = models.ForeignKey('dialogue.Dialogue', on_delete=models.SET_NULL, null=True, related_name='dialogue_task_re')
    task_status = models.IntegerField(choices=TaskStatus.choices, default=7)
    change_time = models.DateTimeField(auto_now_add=True)
    objects = TaskManager()

    def get_simple_info(self):
        signer = TimestampSigner()
        if self.task_status == 5:
            current_comment = user.models.CommentTask.objects.filter(comment_task=self)
            if current_comment:
                current_comment = current_comment.all()[0]
            else:
                current_comment = None
        return dict({
            'task_id': signer.sign_object(self.id),
            'name': self.name,
            'task_type': self.task_type,
            'relation_trasaction_id': signer.sign_object(self.relation_transaction.id) if self.relation_transaction else "No relation transaction",
            'description': self.description,
            'send_user': self.sender_user.get_base_info() if self.sender_user else "No sender",
            'receive_user': self.receive_user.get_base_info() if self.receive_user else "No receiver",
            'upload_user': self.upload_user.get_base_info(),
            'dialogue_id_up_se': signer.sign_object(self.dialogue_between_up_sender.id) if self.dialogue_between_up_sender else "No dialogue",
            'dialogue_id_re_se': signer.sign_object(
                self.dialogue_between_re_sender.id) if self.dialogue_between_re_sender else "No dialogue",
            'price': self.price,
            'sender_addr': self.sender_addr.get_basic_info() if self.sender_addr else "No sender addr",
            'receive_addr': self.receive_addr.get_basic_info() if self.receive_addr else "No receive addr",
            'receive_time': str(self.receive_time),
            'ddl_time': str(self.ddl_time),
            'task_status': self.task_status,
            'task_comment': current_comment.get_base_info() if self.task_status == 5 else None
        })

    def get_base_info(self):
        signer = TimestampSigner()
        return dict({
            'task_id': signer.sign_object(self.id),
            'name': self.name,
            'task_type': self.task_type,
            'relation_trasaction_id': signer.sign_object(self.relation_transaction.id) if self.relation_transaction else "No relation transaction",
            'description': self.description,
            'upload_user': self.upload_user.get_base_info(),
            'price': self.price,
            'sender_addr': self.sender_addr.get_basic_info() if self.sender_addr else "No sender addr",
            'receive_addr': self.receive_addr.get_basic_info() if self.receive_addr else "No receive addr",
            'task_status': self.task_status,
        })