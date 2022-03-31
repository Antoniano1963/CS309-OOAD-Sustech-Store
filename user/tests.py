import datetime
import hashlib

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import User,Address,Comment,CommentTask
from commodity.models import ClassLevel1, ClassLevel2, Merchandise
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


class QuestionModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.foo = User.objects.create(
            name='Antoniano1963',
            password=hash_code('123456'),
            email='11912814@mail.sustech.edu.cn'
        )
        cls.foo1 = User.objects.create(
            name='ZJLYYDS',
            password=hash_code('123456'),
            email='11912821@mail.sustech.edu.cn'
        )
    def test_login(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'Antoniano1963', 'password': '123456'})
        self.assertEqual(reponse0.json()['status'], '200')
        self.assertEqual(reponse0.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
        self.client.cookies.clear()
        reponse1 = self.client.post('/api/login0/pc_login/', {'user_email': '11912814@mail.sustech.edu.cn', 'password': '123456'})
        self.assertEqual(reponse1.json()['status'], '200')
        self.assertEqual(reponse1.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
        reponse2 = self.client.post('/api/login0/pc_login/',
                                    {'user_email': '11912814@mail.sustech.edu.cn', 'password': '123456'})
        self.assertEqual(reponse2.json()['status'], '300')
        self.assertEqual(reponse2.json()['message'],'重复登录')
        self.client.cookies.clear()
        reponse3 = self.client.post('/api/login0/pc_login/',
                                    {'user_email': '11912814@mail.sustech.edu.cn'})
        self.assertEqual(reponse3.json()['status'], '400')
        self.assertEqual(reponse3.json()['message'], 'POST字段不全')

    def test_loginout(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        self.client.cookies.clear()
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'Antoniano1963', 'password': '123456'})
        self.assertEqual(reponse0.json()['status'], '200')
        self.assertEqual(reponse0.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
        self.client.cookies.clear()
        reponse1 = self.client.post('/api/login0/logout/', {'user_email': '11912814@mail.sustech.edu.cn', 'password': '123456'})
        # self.assertEqual(reponse1.json()['status'], '200')
        # self.assertEqual(reponse1.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
        reponse2 = self.client.post('/api/login0/pc_login/',
                                    {'user_email': '11912814@mail.sustech.edu.cn', 'password': '123456'})
        self.assertEqual(reponse2.json()['status'], '200')
        self.assertEqual(reponse2.json()['message'],"用户 {} 登陆成功".format('Antoniano1963'))
        self.client.cookies.clear()

    def test_activate(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        self.client.cookies.clear()
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'Antoniano1963', 'password': '123456'})
        self.assertEqual(reponse0.json()['status'], '200')
        self.assertEqual(reponse0.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
        reponse1 = self.client.post('/api/login0/activate/',
                                    {'real_name': 'lhz',
                                     'self_description': 'a little mouse',
                                     'pay_password': '123321',
                                     'user_identify': 1
                                        })
        self.assertEqual(reponse1.json()['status'], '200')
        self.assertEqual(reponse1.json()['message'], "激活成功")
        reponse2 = self.client.post('/api/login0/activate/',
                                    {'real_name': 'lhz',
                                     'self_description': 'a little mouse',
                                     'pay_password': '123321',
                                     'user_identify': 1
                                     })
        self.assertEqual(reponse2.json()['status'], '400')
        self.assertEqual(reponse2.json()['message'], "用户状态错误")


    def test_addAddress_send(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        self.client.cookies.clear()
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'Antoniano1963', 'password': '123456'})
        self.assertEqual(reponse0.json()['status'], '200')
        self.assertEqual(reponse0.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
        reponse1 = self.client.post('/api/login0/activate/',
                                    {'real_name': 'lhz',
                                     'self_description': 'a little mouse',
                                     'pay_password': '123321',
                                     'user_identify': 1
                                        })
        self.assertEqual(reponse1.json()['status'], '200')
        self.assertEqual(reponse1.json()['message'], "激活成功")
        reponse2 = self.client.post('/api/login0/add_address/',
                                    {'user_name': 'lhz',
                                     'user_addr': 'a little mouse',
                                     'user_phone': '15941121285',
                                     'region_id': 1,
                                     })
        self.assertEqual(reponse2.json()['status'], '200')
        self.assertEqual(reponse2.json()['message'], "成功")


    def test_upload_QR_Code(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        with open('user/1.jpg', 'rb') as fp:
            self.client.cookies.clear()
            reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'Antoniano1963', 'password': '123456'})
            self.assertEqual(reponse0.json()['status'], '200')
            self.assertEqual(reponse0.json()['message'], "用户 {} 登陆成功".format('Antoniano1963'))
            reponse1 = self.client.post('/api/login0/activate/',
                                        {'real_name': 'lhz',
                                         'self_description': 'a little mouse',
                                         'pay_password': '123321',
                                         'user_identify': 1
                                            })
            self.assertEqual(reponse1.json()['status'], '200')
            self.assertEqual(reponse1.json()['message'], "激活成功")
            reponse3 = self.client.post('/api/login0/add_address/',
                                        {'user_name': 'lhz',
                                         'user_addr': 'a little mouse',
                                         'user_phone': '15941121285',
                                         'region_id': 1,
                                         })
            self.assertEqual(reponse3.json()['status'], '200')
            self.assertEqual(reponse3.json()['message'], "成功")
            response4 = self.client.post('/api/login0/get_address_list/',
                                        {'user_name': 'lhz',
                                         'user_addr': 'a little mouse',
                                         'user_phone': '15941121285',
                                         'region_id': 1,
                                         })
            addr_id = response4.json()['return_list'][0]['addr_id']
            image = Image.open(fp)
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            thumb_img = InMemoryUploadedFile(
                file=buffer,
                field_name='thumb',
                name="thumb.png",
                content_type='image/jpeg',
                size=buffer.tell(),
                charset=None
            )
            reponse2 = self.client.post('/api/login0/upload_QR_Code/',
                                        {'mer_name': 'lhz',
                                         'mer_description': 'a little mouse',
                                         'mer_price': 20.0,
                                         'class1_id': 1,
                                         'class2_id': 1,
                                         'fineness_id': 1,
                                         'deliver_price': 10.0,
                                         'send_address_id': addr_id,
                                         'allow_face_trade': True,
                                         'QR_Code': fp
                                         })
            self.assertEqual(reponse2.json()['status'], '200')
            # self.assertEqual(reponse2.json()['message'], "用户状态错误")






