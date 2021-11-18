"""
ASGI config for Final_Project1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
from django.core.asgi import get_asgi_application

from django.core.asgi import get_asgi_application



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Final_Project1.settings')


# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})


def include_Class_Type():
    import commodity.models
    class_list = commodity.models.ClassLevel1.objects.filter(name__exact=1)
    if class_list:
        return True
    class1_1 =  commodity.models.ClassLevel1.objects.create(
        name=1,
        name_str='运动户外'
    )
    class1_2 = commodity.models.ClassLevel1.objects.create(
        name=2,
        name_str='生活用品'
    )
    class1_3 =commodity.models.ClassLevel1.objects.create(
        name=3,
        name_str='电器'
    )
    class1_4 = commodity.models.ClassLevel1.objects.create(
        name=4,
        name_str='数码'
    )
    class1_5 = commodity.models.ClassLevel1.objects.create(
        name=5,
        name_str='服装'
    )
    class1_6 = commodity.models.ClassLevel1.objects.create(
        name=6,
        name_str='美妆'
    )
    class1_7 = commodity.models.ClassLevel1.objects.create(
        name=7,
        name_str='家具'
    )
    class1_8 = commodity.models.ClassLevel1.objects.create(
        name=8,
        name_str='玩具'
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=1,
        name_str='运动服',
        parent_class=class1_1,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=2,
        name_str='运动鞋',
        parent_class=class1_1,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=3,
        name_str='五金用品',
        parent_class=class1_2,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=4,
        name_str='办公用品',
        parent_class=class1_2,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=5,
        name_str='办公设备',
        parent_class=class1_2,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=6,
        name_str='大家电',
        parent_class=class1_3,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=7,
        name_str='厨房电器',
        parent_class=class1_3,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=8,
        name_str='生活电器',
        parent_class=class1_3,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=9,
        name_str='电脑',
        parent_class=class1_4,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=10,
        name_str='电脑配件',
        parent_class=class1_4,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=11,
        name_str='智能设备',
        parent_class=class1_4,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=12,
        name_str='手机',
        parent_class=class1_4,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=13,
        name_str='相机',
        parent_class=class1_4,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=14,
        name_str='上衣',
        parent_class=class1_5,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=15,
        name_str='外套',
        parent_class=class1_5,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=16,
        name_str='美容护肤',
        parent_class=class1_6,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=17,
        name_str='彩妆',
        parent_class=class1_6,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=18,
        name_str='香水',
        parent_class=class1_6,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=19,
        name_str='家具饰品',
        parent_class=class1_7,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=20,
        name_str='住宅家具',
        parent_class=class1_7,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=21,
        name_str='模型',
        parent_class=class1_8,
    )
    class2_1 = commodity.models.ClassLevel2.objects.create(
        name=22,
        name_str='手办',
        parent_class=class1_8,
    )
