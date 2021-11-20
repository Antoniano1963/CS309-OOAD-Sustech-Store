import os

from django.contrib.postgres.fields import ArrayField
from django.core.signing import TimestampSigner
from django.db import models
from django.utils.translation import gettext_lazy as _
import django.utils.timezone
from Final_Project1.settings import MEDIA_ROOT, FILE_URL
# Create your models here.

file_url = FILE_URL


class MerchandiseManager(models.Manager):
    def get_merchandises_by_class(self, class1_id, class2_id, fineness_id=None, sort='default'):
        '''根据商品类型id查询商品信息'''
        if sort == 'new':
            order_by = ('-upload_date',)
        elif sort == 'hot':
            order_by = ('-favourite_number',)
        elif sort == 'price':
            order_by = ('price',)
        elif sort == '-new':
            order_by = ('upload_date',)
        elif sort == '-hot':
            order_by = ('favourite_number',)
        elif sort == '-price':
            order_by = ('-price',)
        else:
            order_by = ('-pk',)  # 按照primary key降序排列。

        # 查询数据
        if fineness_id:
            books_li = self.filter(status__exact=1).filter(class_level_1_id__exact=class1_id).filter(
                class_level_2_id__exact=class2_id).filter(fineness__exact=fineness_id).order_by(*order_by)
        else:
            books_li = self.filter(status__exact=1).filter(class_level_1_id__exact=class1_id).filter(class_level_2_id__exact=class2_id).order_by(*order_by)
        return books_li

    def get_merchandises_only_by_class1(self, class1_id, fineness_id=None, sort='default'):
        '''根据商品类型id查询商品信息'''
        if sort == 'new':
            order_by = ('-upload_date',)
        elif sort == 'hot':
            order_by = ('-favourite_number',)
        elif sort == 'price':
            order_by = ('price',)
        elif sort == '-new':
            order_by = ('upload_date',)
        elif sort == '-hot':
            order_by = ('favourite_number',)
        elif sort == '-price':
            order_by = ('-price',)
        else:
            order_by = ('-pk',)  # 按照primary key降序排列。

        # 查询数据
        if fineness_id:
            books_li = self.filter(status__exact=1).filter(class_level_1_id__exact=class1_id).filter(fineness__exact=fineness_id).order_by(*order_by)
        else:
            books_li = self.filter(status__exact=1).filter(class_level_1_id__exact=class1_id).order_by(*order_by)
        # 查询结果集的限制
        return books_li


class Merchandise(models.Model):
    def user_directory_path(instance, filename):
        return 'user_{0}\\user_{1}_mer\\upload_merchandise_[2]_time:_{3}_{4}'.format(instance.upload_user.id, instance.upload_user.id, instance.id, django.utils.timezone.now(), filename)

    def user_thumb_directory_path(instance, filename):
        return 'user_{0}\\user_{1}_thumb\\upload_merchandise_[2]_time:_{3}_{4}'.format(instance.upload_user.id, instance.upload_user.id, instance.id, django.utils.timezone.now(), filename)

    class MerchandiseStatus(models.IntegerChoices):
        ONSALLING = (1, '正在售卖')
        ONTRANSACTION = (2, '正在交易')
        PROBLEM = (3, '出现问题')
        SALLED = (4, '已经售出')
        POSTTRA = (5, '被订单锁定')
        DELETE = (0, '已删除')

    class Fineness(models.IntegerChoices):
        NEW = (1, '全新')
        ALMOST_NEW = (2, '几乎全新')
        USED = (3, '轻微使用痕迹')
        DEEP_USED = (4, '明显使用痕迹')

    name = models.CharField(max_length=128)
    upload_date = models.DateTimeField(auto_now_add=True)
    upload_user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="merchandises",)
    description = models.TextField(null=True)
    image1 = models.ImageField(upload_to=user_directory_path, null=True, max_length=409600)
    image2 = models.ImageField(upload_to=user_directory_path, null=True, max_length=409600)
    image3 = models.ImageField(upload_to=user_directory_path, null=True, max_length=409600)
    price = models.FloatField()
    deliver_price = models.FloatField(default=0)
    sender_addr = models.ForeignKey('user.Address', on_delete=models.SET_NULL, related_name="addr_mer_0", null=True)
    thumb = models.ImageField(upload_to=user_thumb_directory_path, null=True, max_length=102400)
    class_level_1 = models.ForeignKey("ClassLevel1", on_delete=models.CASCADE, related_name="mer_class1", null=True)
    class_level_2 = models.ForeignKey("ClassLevel2", on_delete=models.CASCADE, related_name="mer_class2", null=True)
    fineness = models.IntegerField(choices=Fineness.choices, default=1)
    status = models.IntegerField(choices=MerchandiseStatus.choices, default=1)
    favourite_number = models.IntegerField(default=0)
    objects = MerchandiseManager()
    allow_face_trade = models.BooleanField(default=True)
    browse_number = models.IntegerField(default=0)
    who_favourite = ArrayField(
        base_field=models.IntegerField(),
        blank=True,
        default=list
    )

    class Meta:
        unique_together = ['name', 'upload_user']

    def get_avatar_url1(self):
        '''返回头像的url'''
        return os.path.join(MEDIA_ROOT, str(self.image1))

    def get_avatar_url2(self):
        '''返回头像的url'''
        return os.path.join(MEDIA_ROOT, str(self.image2))

    def get_avatar_url3(self):
        '''返回头像的url'''
        return os.path.join(MEDIA_ROOT, str(self.image3))

    def get_thumb_url(self):
        '''返回头像的url'''
        return os.path.join(MEDIA_ROOT, str(self.thumb))


    def __str__(self):
        return self.name

    def get_simple_info(self):
        mer_image_url = self.get_thumb_url().replace('/', '\\')
        info = dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': mer_image_url
        })
        signer = TimestampSigner()
        return dict({
            'mer_id': signer.sign_object(self.id),
            'mer_name': self.name,
            'mer_price': self.price,
            'deliver_price': self.deliver_price,
            'mer_description': self.description,
            'mer_img_url': f"{file_url}{signer.sign_object(info)}",
            # 'mer_Img': i.image1.open(),
            'mer_upload_user_id': signer.sign_object(self.upload_user.id),
            'mer_upload_user_name': self.upload_user.name,
            'favourite_number': self.favourite_number,
            'allow_face_trade': self.allow_face_trade,
            'browse_number': self.browse_number,
            'as_favorite_number': len(self.who_favourite),
            'mer_status': self.status,
        })

    def get_details(self):
        mer_image_url1 = self.get_avatar_url1().replace('/', '\\')
        info1 = dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': mer_image_url1
        })
        mer_image_url2 = self.get_avatar_url2().replace('/', '\\')
        info2 = dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': mer_image_url2
        })
        mer_image_url3 = self.get_avatar_url3().replace('/', '\\')
        info3 = dict({
            'mer_id': self.id,
            'date': str(django.utils.timezone.now()),
            'path': mer_image_url3
        })
        has_img2 = False
        has_img3 = False
        if not self.image2:
            has_img2 = True
        if not self.image3:
            has_img3 = True
        signer = TimestampSigner()
        return dict({
            'mer_id': signer.sign_object(self.id),
            'mer_name': self.name,
            'mer_price': self.price,
            'mer_update': self.upload_date,
            'mer_description': self.description,
            'mer_upload_user_id': signer.sign_object(self.upload_user.id),
            'mer_upload_user_name': self.upload_user.name,
            'mer_img_url': f"{file_url}{signer.sign_object(info1)}",
            'mer_img_url2': f"{file_url}{signer.sign_object(info2)}",
            'mer_img_url3': f"{file_url}{signer.sign_object(info3)}",
            'has_img2': has_img2,
            'has_img3': has_img3,
            'favourite_number': self.favourite_number,
            'fineness_id': self.fineness,
            'browse_number': self.browse_number,
            'as_favorite_number': len(self.who_favourite),
            'mer_status': self.status,
        })


class ClassLevel1(models.Model):

    class Class_Level_1(models.IntegerChoices):
        class_l1_1 = (1, '运动户外')
        class_l1_2 = (2, '生活用品')
        class_l1_3 = (3, '电器')
        class_l1_4 = (4, '数码')
        class_l1_5 = (5, '服装')
        class_l1_6 = (6, '美妆')
        class_l1_7 = (7, '家具')
        class_l1_8 = (8, '玩具')

    class Class_Level_1_str(models.TextChoices):
        class_l1_1 = ('运动户外', '运动户外')
        class_l1_2 = ('生活用品', '生活用品')
        class_l1_3 = ('电器', '电器')
        class_l1_4 = ('数码', '数码')
        class_l1_5 = ('服装', '服装')
        class_l1_6 = ('美妆', '美妆')
        class_l1_7 = ('家具', '家具')
        class_l1_8 = ('玩具', '玩具')
    name = models.IntegerField(choices=Class_Level_1.choices, default=1)
    name_str = models.CharField(choices=Class_Level_1_str.choices, default='运动户外', max_length=256)


class ClassLevel2(models.Model):

    class Class_Level_2(models.IntegerChoices):
        class_l2_1 = (1, '运动服')
        class_l2_2 = (2, '运动鞋')
        class_l2_3 = (3, '五金用品')
        class_l2_4 = (4, '办公用品')
        class_l2_5 = (5, '办公设备')
        class_l2_6 = (6, '大家电')
        class_l2_7 = (7, '厨房电器')
        class_l2_8 = (8, '生活电器')
        class_l2_9 = (9, '电脑')
        class_l2_10 = (10, '电脑配件')
        class_l2_11 = (11, '智能设备')
        class_l2_12 = (12, '手机')
        class_l2_13 = (13, '相机')
        class_l2_14 = (14, '上衣')
        class_l2_15 = (15, '外套')
        class_l2_16 = (16, '美容护肤')
        class_l2_17 = (17, '彩妆')
        class_l2_18 = (18, '香水')
        class_l2_19 = (19, '家具饰品')
        class_l2_20 = (20, '住宅家具')
        class_l2_21 = (21, '模型')
        class_l2_22 = (22, '手办')

    class Class_Level_2_str(models.TextChoices):
        class_l2_1 = ('运动服', '运动服')
        class_l2_2 = ('运动鞋', '运动鞋')
        class_l2_3 = ('五金用品', '五金用品')
        class_l2_4 = ('办公用品', '办公用品')
        class_l2_5 = ('办公设备', '办公设备')
        class_l2_6 = ('大家电', '大家电')
        class_l2_7 = ('厨房电器', '厨房电器')
        class_l2_8 = ('生活电器', '生活电器')
        class_l2_9 = ('电脑', '电脑')
        class_l2_10 = ('电脑配件', '电脑配件')
        class_l2_11 = ('智能设备', '智能设备')
        class_l2_12 = ('手机', '手机')
        class_l2_13 = ('相机', '相机')
        class_l2_14 = ('上衣', '上衣')
        class_l2_15 = ('外套', '外套')
        class_l2_16 = ('美容护肤', '美容护肤')
        class_l2_17 = ('彩妆', '彩妆')
        class_l2_18 = ('香水', '香水')
        class_l2_19 = ('家具饰品', '家具饰品')
        class_l2_20 = ('住宅家具', '住宅家具')
        class_l2_21 = ('模型', '模型')
        class_l2_22 = ('手办', '手办')
    name = models.IntegerField(choices=Class_Level_2.choices, default=1)
    name_str = models.CharField(choices=Class_Level_2_str.choices, default='运动服', max_length=256)
    parent_class = models.ForeignKey("ClassLevel1", on_delete=models.CASCADE, related_name="child_class")
