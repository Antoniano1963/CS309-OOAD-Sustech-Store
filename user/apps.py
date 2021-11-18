from django.apps import AppConfig

from channels.db import database_sync_to_async
from django.apps import AppConfig
from django.db.models.signals import post_migrate



def add_address(sender, **kwargs):
    import user.models

    address_list = user.models.Address.objects.filter(user_name__contains='系统')
    if not address_list:
        user0 = user.models.User.objects.create(

        )
        address1 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=1,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address2 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=2,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address3 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=3,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address4 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=4,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address5 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=5,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address6 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=6,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address7 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=7,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address8 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=8,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address9 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=9,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address10 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=10,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address11 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=11,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address12 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=12,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address13 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=13,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address14 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=14,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address15 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=15,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address16 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=16,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address17 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=17,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address18 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=18,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address19 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=19,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address20 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=20,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address21 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=21,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address22 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=22,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address23 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=23,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address24 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=24,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address25 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=25,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address26 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=26,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address27 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=27,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address28 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=28,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address29 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=29,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )
        address30 = user.models.Address.objects.create(
            user_name='系统',
            user_addr='',
            region=30,
            addr_type=1,
            relate_number=0,
            user_phone='00000000',
            user=user0,
            address_role=2
        )


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    # def ready(self):
        # post_migrate.connect(add_address, sender=self)
