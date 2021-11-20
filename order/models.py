import os

from django.db import models
import user.models

# Create your models here.
from django.core.signing import TimestampSigner
import django.utils.timezone

from Final_Project1.settings import MEDIA_ROOT, FILE_URL


file_url = FILE_URL

class Transaction(models.Model):

    def tra_directory_path(instance, filename):
        return 'tra_{0}/pay_prove_upload_time:_{1}_{2}'.format(instance.id, django.utils.timezone.now(), filename)

    class TransactionStatus(models.IntegerChoices):
        CANCEL = (0, '已取消')
        WAITPAYMENT = (1, '等待付款')
        WAITDELIVER = (2, '等待发货')
        WAITRECEIVING = (3, '等待收货')
        WAITCOMMENT = (4, '等待评价')
        FINISH = (5, '已送达')
        DISPUTE = (6, '有争议')
        QRWAIT = (7, '二维码支付等待确认')
        SOVED = (8, '争议解决')

    class QRPayStatus(models.IntegerChoices):
        INITIAL = (1, '初始状态')
        WAITCONFIRM = (2, '等待卖家确认')
        ALREADYFONFIRM = (3, '卖家已经确认')

    PAY_METHOD_CHOICES = (
        (1, "货到付款"),
        (2, "二维码支付"),
        (3, "虚拟货币")
    )

    transaction_sender = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='sender_transactions')
    transaction_receiver = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='receiver_Transactions')
    transaction_merchandise = models.ForeignKey('commodity.Merchandise', on_delete=models.CASCADE, related_name='merc_Transactions')
    status = models.IntegerField(choices=TransactionStatus.choices, null=False, default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    pay_time = models.DateTimeField(null=True)
    comfirm_time = models.DateTimeField(null=True)
    send_time = models.DateTimeField(null=True)
    receive_time = models.DateTimeField(null=True)
    sender_location = models.ForeignKey('user.Address', on_delete=models.CASCADE, related_name='locations_to_sender_tr')
    receiver_location = models.ForeignKey('user.Address', on_delete=models.CASCADE, related_name='locations_to_receiver_tr')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=1, verbose_name='支付方式',null=True)
    trade_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付编号')
    transaction_price = models.FloatField(default=0)
    total_price = models.FloatField()
    QR_pay_status = models.IntegerField(choices=QRPayStatus.choices, default=1)
    has_task = models.BooleanField(default=False)
    has_problem = models.BooleanField(default=False)
    rela_problem_id = models.IntegerField(default=-1)
    rela_problem_type = models.IntegerField(default=-1)
    rela_problem_description = models.CharField(max_length=128, null=True)
    has_problem_before = models.BooleanField(default=False)
    pay_prove = models.ImageField(max_length=409600, upload_to=tra_directory_path, null=True)

    def get_simple_overview(self):
        signer = TimestampSigner()
        if self.status == 5:
            current_comment = user.models.Comment.objects.filter(comment_transaction=self)
            if current_comment:
                current_comment = current_comment.all()[0]
            else:
                current_comment = None
        return dict({
            'transaction_id': signer.sign_object(self.id),
            'transaction_sender_id': signer.sign_object(self.transaction_sender.id),
            'transaction_receiver_id': signer.sign_object(self.transaction_receiver.id),
            'transaction_sender_name': self.transaction_sender.name,
            'transaction_receiver_name': self.transaction_receiver.name,
            'transaction_status': self.status,
            'transaction_price': self.total_price,
            'merchandise_id': signer.sign_object(self.transaction_merchandise.id),
            'merchandise_name': self.transaction_merchandise.name,
            'merchandise_price': self.transaction_merchandise.price,
            'receiver_location': self.receiver_location.get_basic_info(),
            'sender_location': self.sender_location.get_basic_info(),
            'merchandise_info': self.transaction_merchandise.get_simple_info(),
            'create_time': str(self.create_time),
            'has_task': self.has_task,
            'transaction_comment': current_comment.get_base_info() if self.status == 5 else None,
            'has_problem': self.has_problem,
            'problem_type': self.rela_problem_type,
            'problem_id': signer.sign_object(self.rela_problem_id),
            'problem_description': self.rela_problem_description,
            'has_problem_before': self.has_problem_before,
            'pay_prove': f"{file_url}{signer.sign_object(self.get_pay_prove_info())}",
            'pay_method': self.pay_method,
        })

    def get_basic_overview(self):
        signer = TimestampSigner()
        return dict({
            'transaction_id': signer.sign_object(self.id),
            'transaction_sender_id': signer.sign_object(self.transaction_sender.id),
            'transaction_receiver_id': signer.sign_object(self.transaction_receiver.id),
            'transaction_price': self.total_price,
            'merchandise_id': signer.sign_object(self.transaction_merchandise.id),
            'merchandise_name': self.transaction_merchandise.name,
            'merchandise_price': self.transaction_merchandise.price,
            'merchandise_info': self.transaction_merchandise.get_simple_info(),
            'has_task': self.has_task,
            'has_problem': self.has_problem,
            'has_problem_before': self.has_problem_before,
            'pay_method': self.pay_method,
        })

    def get_pay_prove_info(self):
        QRCode_url = os.path.join(MEDIA_ROOT, str(self.pay_prove))
        return dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': QRCode_url
        })


class TransactionProblem(models.Model):
    class ProblemType(models.IntegerChoices):
        TYPE1 = (1, '申请退货')
        TYPE2 = (2, '线下交易冲突')
        TYPE3 = (3, '二维码未收款')
        TYPE4 = (4, '恶意未发货')
        TYPE5 = (5, '卖家问题')
    class ProblemRole(models.IntegerChoices):
        USER = (1, '用户')
        BUSINESS = (2, '卖家')
    class ProblemStatus(models.IntegerChoices):
        WAIT = (1, '等待处理')
        FINISH = (2, '完成')
    problem_description = models.CharField(max_length=512)
    problem_upload_date = models.DateTimeField(auto_now_add=True)
    problem_transaction = models.ForeignKey('order.Transaction', on_delete=models.CASCADE, related_name='transaction_rela_problem')
    problem_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="user_upload_problem")
    problem_type = models.IntegerField(choices=ProblemType.choices)
    superuser_log = models.CharField(max_length=1024, null=True, blank=True)
    handle_superuser = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="superuser_rela_problem", null=True)
    handle_date = models.DateTimeField(null=True)
    problem_role = models.IntegerField(choices=ProblemRole.choices, null=True)
    problem_user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="user_rela_problem", null=True)
    problem_status = models.IntegerField(choices=ProblemStatus.choices, default=1)
    transaction_last_status = models.IntegerField(default=1)

    def get_detail_info(self):
        signer = TimestampSigner()
        return dict({
            'problem_id': signer.sign_object(self.id),
            'problem_description': self.problem_description,
            'problem_upload_date': self.problem_upload_date,
            'problem_transaction':self.problem_transaction.get_simple_overview(),
            'problem_uploader': self.problem_uploader.get_base_info(),
            'problem_type': self.problem_type,
            'superuser_log': self.superuser_log,
            'handle_date': self.handle_date,
            'handle_superuser': self.handle_superuser.get_base_info() if self.handle_superuser else 'No superuser',

        })







