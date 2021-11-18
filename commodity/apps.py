from channels.db import database_sync_to_async
from django.apps import AppConfig
from django.db.models.signals import post_migrate



def add_class(sender, **kwargs):
    import commodity.models
    class_list = commodity.models.ClassLevel1.objects.filter(name__exact=1)
    if not class_list:
        class1_1 = commodity.models.ClassLevel1.objects.create(
            id=1,
            name=1,
            name_str='运动户外'
        )
        class1_2 = commodity.models.ClassLevel1.objects.create(
            id=2,
            name=2,
            name_str='生活用品'
        )
        class1_3 = commodity.models.ClassLevel1.objects.create(
            id=3,
            name=3,
            name_str='电器'
        )
        class1_4 = commodity.models.ClassLevel1.objects.create(
            id=4,
            name=4,
            name_str='数码'
        )
        class1_5 = commodity.models.ClassLevel1.objects.create(
            id=5,
            name=5,
            name_str='服装'
        )
        class1_6 = commodity.models.ClassLevel1.objects.create(
            id=6,
            name=6,
            name_str='美妆'
        )
        class1_7 = commodity.models.ClassLevel1.objects.create(
            id=7,
            name=7,
            name_str='家具'
        )
        class1_8 = commodity.models.ClassLevel1.objects.create(
            id=8,
            name=8,
            name_str='玩具'
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=1,
            name=1,
            name_str='运动服',
            parent_class=class1_1,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=2,
            name=2,
            name_str='运动鞋',
            parent_class=class1_1,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=3,
            name=3,
            name_str='五金用品',
            parent_class=class1_2,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=4,
            name=4,
            name_str='办公用品',
            parent_class=class1_2,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=5,
            name=5,
            name_str='办公设备',
            parent_class=class1_2,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=6,
            name=6,
            name_str='大家电',
            parent_class=class1_3,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=7,
            name=7,
            name_str='厨房电器',
            parent_class=class1_3,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=8,
            name=8,
            name_str='生活电器',
            parent_class=class1_3,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=9,
            name=9,
            name_str='电脑',
            parent_class=class1_4,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=10,
            name=10,
            name_str='电脑配件',
            parent_class=class1_4,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=11,
            name=11,
            name_str='智能设备',
            parent_class=class1_4,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=12,
            name=12,
            name_str='手机',
            parent_class=class1_4,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=13,
            name=13,
            name_str='相机',
            parent_class=class1_4,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=14,
            name=14,
            name_str='上衣',
            parent_class=class1_5,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=15,
            name=15,
            name_str='外套',
            parent_class=class1_5,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=16,
            name=16,
            name_str='美容护肤',
            parent_class=class1_6,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=17,
            name=17,
            name_str='彩妆',
            parent_class=class1_6,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=18,
            name=18,
            name_str='香水',
            parent_class=class1_6,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=19,
            name=19,
            name_str='家具饰品',
            parent_class=class1_7,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=20,
            name=20,
            name_str='住宅家具',
            parent_class=class1_7,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=21,
            name=21,
            name_str='模型',
            parent_class=class1_8,
        )
        class2_1 = commodity.models.ClassLevel2.objects.create(
            id=22,
            name=22,
            name_str='手办',
            parent_class=class1_8,
        )


class CommodityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'commodity'
    def ready(self):
        post_migrate.connect(add_class, sender=self)