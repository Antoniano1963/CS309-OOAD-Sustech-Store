from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.signing import TimestampSigner
import django
from Final_Project1.settings import MEDIA_ROOT
import os
import django.utils.timezone
# Create your models here.

file_url = "http://store.sustech.xyz:8080/api/commodity/download/?key="


class User(models.Model):
    '''用户表'''
    def user_directory_path(instance, filename):
        return 'user_{0}\\user_{1}_self\\QRCode_upload_time:_{2}_{3}'.format(instance.id, instance.id, django.utils.timezone.now(), filename)

    def user_directory_path2(instance, filename):
        return 'user_{0}\\user_{1}_self\\Header_photo_upload_time:_{2}_{3}'.format(instance.id, instance.id, django.utils.timezone.now(), filename)

    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    class UserStatus(models.IntegerChoices):
        CANCEL = (0, '未激活')
        WAITPAYMENT = (1, '可以购买')
        WAITDELIVER = (2, '可以上传商品')


    class Identify(models.IntegerChoices):
        SUPERUSER = (0, '系统管理员')
        STUDENT = (1, '本科生')
        MASTER = (2, '研究生')
        DOCTOR = (3, '博士生')
        WORKER = (4, '教职工')

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True, blank=False)
    c_time = models.DateTimeField(auto_now_add=True)
    money_receiving_QR_code = models.ImageField(upload_to=user_directory_path, null=True, max_length=409600)
    money = models.FloatField(default=0)
    wait_notice = models.IntegerField(default=0)
    header_photo = models.ImageField(upload_to=user_directory_path2, null=True, max_length=409600)
    user_status = models.IntegerField(choices=UserStatus.choices, default=0)
    real_name = models.CharField(max_length=64, null=True)
    user_identify = models.IntegerField(choices=Identify.choices, null=True)
    self_description = models.CharField(max_length=512, null=True)
    sold_goods_number = models.IntegerField(default=0)
    uploaded_goods_numbers = models.IntegerField(default=0)
    pay_password = models.CharField(max_length=256, null=True, blank=True)
    stars_for_deliver = models.FloatField(default=5)
    stars_for_good = models.FloatField(default=5)
    stars_for_attitude = models.FloatField(default=5)
    comment_number = models.IntegerField(default=0)
    SID = models.IntegerField(default=0)
    stars_for_task = models.IntegerField(default=5)
    comment_number_for_task = models.IntegerField(default=0)
    has_header_photo = models.BooleanField(default=False)
    problem_number = models.IntegerField(default=0)
    as_favorite_business_number = models.IntegerField(default=0)
    notice_info_unread = ArrayField(
        base_field=models.JSONField(),
        blank=True,
        default=list
    )
    notice_info = ArrayField(
        base_field=models.JSONField(),
        blank=True,
        default=list
    )
    favorite_sellers = ArrayField(
        base_field=models.IntegerField(),
        size=128,
        blank=True,
        default=list
    )
    favorite_merchandise = ArrayField(
        base_field=models.IntegerField(),
        size=128,
        blank=True,
        default=list
    )
    user_transactions = ArrayField(
        base_field=models.IntegerField(),
        blank=True,
        default=list
    )
    user_recommend_list = ArrayField(
        base_field=models.IntegerField(),
        blank=True,
        default=list
    )

    def get_base_info(self):
        header_photo_url = self.get_Header_Photo_url().replace('/', '\\')
        info = dict({
            'user_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': header_photo_url
        })
        signer = TimestampSigner()
        return dict({
            'user_id': signer.sign_object(self.id),
            'user_name': self.name,
            # 'user_email': self.email,
            'user_identify': self.user_identify,
            'self_description': self.self_description,
            'header_photo_url': signer.sign_object(info),
            'uploaded_goods_number': self.uploaded_goods_numbers,
            'sold_goods_number': self.sold_goods_number,
            "total_star": self.stars_for_good*0.5 + self.stars_for_deliver*0.3 + self.stars_for_attitude*0.2,
            'has_header_photo': self.has_header_photo,
            'as_favorite_business_number': self.as_favorite_business_number,
        })

    def get_simple_info(self):
        header_photo_url = self.get_Header_Photo_url().replace('/', '\\')
        info = dict({
            'user_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': header_photo_url
        })
        signer = TimestampSigner()
        return dict({
            'user_id': signer.sign_object(self.id),
            'user_name': self.name,
            'user_email': self.email,
            'user_real_name': self.real_name,
            'user_status': self.user_status,
            'user_identify': self.user_identify,
            'self_description': self.self_description,
            'header_photo_url': signer.sign_object(info),
            'uploaded_goods_number': self.uploaded_goods_numbers,
            'sold_goods_number': self.sold_goods_number,
            "total_start": self.stars_for_good * 0.5 + self.stars_for_deliver * 0.3 + self.stars_for_attitude * 0.2,
            'stars_for_deliver': self.stars_for_deliver,
            'stars_for_attitude': self.stars_for_attitude,
            'stars_for_good': self.stars_for_good,
            'stars_for_task': self.stars_for_task,
            'comment_number': self.comment_number,
            'money': self.money,
            'has_header_photo': self.has_header_photo,
            'as_favorite_business_number': self.as_favorite_business_number,
        })

    def get_ORCode_url(self):
        '''返回头像的url'''
        return os.path.join(MEDIA_ROOT, str(self.money_receiving_QR_code))

    def get_Header_Photo_url(self):
        '''返回头像的url'''
        return os.path.join(MEDIA_ROOT, str(self.header_photo))

    def get_QRCode_info(self):
        QRCode_url = self.get_ORCode_url().replace('/', '\\')
        return dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': QRCode_url
        })

    def get_Header_Photo_info(self):
        header_photo_url = self.get_ORCode_url().replace('/', '\\')
        return dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': header_photo_url
        })

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']


class AddressManager(models.Manager):
    '''地址模型管理器类'''
    def get_default_address(self, user_id):
        '''查询指定用户的默认收货地址'''
        try:
            addr = self.get(user_id__exact=user_id, is_default=True)
        except self.model.DoesNotExist:
            # 没有默认收货地址
            addr = None
        return addr

    def add_one_address(self, user_id, recipient_name, recipient_addr, zip_code, recipient_phone):
        '''添加收货地址'''
        # 判断用户是否有默认收货地址
        addr = self.get_default_address(user_id=user_id)

        if addr:
            # 存在默认地址
            is_default = False
        else:
            # 不存在默认地址
            is_default = True

        # 添加一个地址
        addr = self.create(user_id=user_id,
                           user_name=recipient_name,
                           user_addr=recipient_addr,
                           user_phone=recipient_phone,
                           is_default=is_default)
        return addr


class Address(models.Model):

    class Region(models.IntegerChoices):
        REGION1 = (1, '荔园')
        REGION2 = (2, '创园')
        REGION3 = (3, '慧园')
        REGION4 = (4, '欣园')
        REGION5 = (5, '学生宿舍')
        REGION6 = (6, '湖畔')
        REGION7 = (7, '九华精舍')
        REGION8 = (8, '教师公寓')
        REGION9 = (9, '专家公寓')
        REGION10 = (10, '风雨操场')
        REGION11 = (11, '润扬体育馆')
        REGION12 = (12, '工学院')
        REGION13 = (13, '南科大中心')
        REGION14 = (14, '第一科研楼')
        REGION15 = (15, '第二科研楼')
        REGION16 = (16, '第一教学楼')
        REGION17 = (17, '第二教学楼')
        REGION18 = (18, '台州楼')
        REGION19 = (19, '检测中心')
        REGION20 = (20, '行政楼')
        REGION21 = (21, '琳恩图书馆')
        REGION22 = (22, '1号门')
        REGION23 = (23, '2号门')
        REGION24 = (24, '3号门')
        REGION25 = (25, '4号门')
        REGION26 = (26, '5号门')
        REGION27 = (27, '6号门')
        REGION28 = (28, '7号门')
        REGION29 = (29, '8号门')
        REGION30 = (30, '其他')

    class AddressType(models.IntegerChoices):
        RECEIVE = (1, '收货')
        SENDER = (2, '发货')

    user_name = models.CharField(max_length=20, verbose_name='收件人')
    user_addr = models.CharField(max_length=256, verbose_name='收件地址')
    region = models.IntegerField(choices=Region.choices, default=1)
    addr_type = models.IntegerField(choices=AddressType.choices, default=1)
    relate_number = models.IntegerField(default=0)
    # zip_code = models.CharField(max_length=6, verbose_name='邮政编码')
    user_phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    # passport = models.ForeignKey('Passport', verbose_name='账户')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='address_to_user')
    objects = AddressManager()

    def get_info(self):
        signer = TimestampSigner()
        return dict({
            'addr_id': signer.sign_object(self.id),
            'user_id': signer.sign_object(self.user.id),
            'user_name': self.user_name,
            'user_region': self.region,
            'user_addr': self.user_addr,
            'user_phone': self.user_phone,
            'is_default': self.is_default,
            'address_type':self.addr_type
        })
    def get_basic_info(self):
        signer = TimestampSigner()
        return dict({
            'addr_id': signer.sign_object(self.id),
            'user_id': signer.sign_object(self.user.id),
            'user_name': self.user_name,
            'user_region': self.region,
            'user_addr': self.user_addr,
            # 'user_phone': self.user_phone,
            'is_default': self.is_default
        })


class Comment(models.Model):
    class Level(models.IntegerChoices):
        VERY_BAD = (1, '非常不满')
        BAD = (2, '不满')
        MIDDLE = (3, '一般')
        GOOD = (4, '较为满意')
        GREAT = (5, '十分满意')
    comment_content = models.CharField(max_length=512)
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='user_comment_mer')
    comment_target = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='target_comment_mer')
    comment_transaction = models.ForeignKey('order.Transaction', on_delete=models.CASCADE,
                                            related_name='comments_tra')
    comment_level_mer = models.IntegerField(choices=Level.choices, null=False)
    comment_level_attitude = models.IntegerField(choices=Level.choices, null=False)
    comment_level_tra = models.IntegerField(choices=Level.choices, null=False)
    agree_number = models.IntegerField(default=0)
    disagree_number = models.IntegerField(default=0)
    # sub_comment_number = models.IntegerField(default=0)

    class Meta:
        ordering = ['-agree_number', 'disagree_number']
    # partent = models.IntegerField(null=True)

    def get_detail_info(self):
        signer = TimestampSigner()
        return dict({
            'user_info': self.comment_user.get_base_info(),
            'comment_content': self.comment_content,
            'comment_date': str(self.comment_date),
            'transaction_info': self.comment_transaction.get_simple_overview(),
            'comment_level_mer': self.comment_level_mer,
            'comment_level_attitude': self.comment_level_attitude,
            'comment_level_tra': self.comment_level_tra,
        })


class CommentTask(models.Model):
    class Level(models.IntegerChoices):
        VERY_BAD = (1, '非常不满')
        BAD = (2, '不满')
        MIDDLE = (3, '一般')
        GOOD = (4, '较为满意')
        GREAT = (5, '十分满意')
    comment_content = models.CharField(max_length=512)
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='user_comment_task')
    comment_target = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name='target_comment_task')
    comment_task = models.ForeignKey('task.Task', on_delete=models.CASCADE,
                                            related_name='comments_task')
    comment_level = models.IntegerField(choices=Level.choices, null=False)
    agree_number = models.IntegerField(default=0)
    disagree_number = models.IntegerField(default=0)

    class Meta:
        ordering = ['-agree_number', 'disagree_number']


    def get_detail_info(self):
        signer = TimestampSigner()
        return dict({
            'user_info': self.comment_user.get_base_info(),
            'comment_content': self.comment_content,
            'comment_date': str(self.comment_date),
            'task_info': self.comment_task.get_simple_info(),
            'comment_level': self.comment_level,
        })


