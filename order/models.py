from django.db import models

# Create your models here.
from django.core.signing import TimestampSigner

class Transaction(models.Model):
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

    def get_simple_overview(self):
        signer = TimestampSigner()
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
        })


class TransactionProblem(models.Model):
    class ProblemType(models.IntegerChoices):
        TYPE1 = (1, '申请退货')
        TYPE2 = (2, '线下交易冲突')
        TYPE3 = (3, '二维码未收款')
        TYPE4 = (4, '恶意未发货')
        TYPE5 = (5, '卖家问题')
    class Problemrole(models.IntegerChoices):
        USER = (1, '用户')
        BUSINESS = (2, '卖家')
    problem_description = models.CharField(max_length=512)
    problem_upload_date = models.DateTimeField(auto_now_add=True)
    problem_transaction = models.ForeignKey('order.Transaction', on_delete=models.CASCADE, related_name='transaction_rela_problem')
    problem_uploader = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="user_upload_problem")
    problem_type = models.IntegerField(choices=ProblemType.choices)
    superuser_log = models.CharField(max_length=1024, null=True, blank=True)
    handle_superuser = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="superuser_rela_problem")
    handle_date = models.DateTimeField(null=True)
    problem_role = models.IntegerField(choices=ProblemType.choices, default=2)
    problem_user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="user_rela_problem")

    def get_detail_info(self):
        signer = TimestampSigner()
        return dict({
            'problem_description': self.problem_description,
            'problem_upload_date': self.problem_upload_date,
            'problem_transaction':self.problem_transaction.get_basic_overview(),
            'problem_uploader': self.problem_uploader.get_base_info(),
            'problem_type': self.problem_type,
            'superuser_log': self.superuser_log,
            'handle_date': self.handle_date,
            'handle_superuser': self.handle_superuser.get_base_info(),

        })







