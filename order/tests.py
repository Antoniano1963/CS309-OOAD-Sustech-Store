from django.test import TestCase

# Create your tests here.
import datetime
import hashlib

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import *
from user.models import *
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
            email='11912821@mail.sustech.edu.cn',
            pay_password='123321'
        )
        # {'mer_name': 'lhz',
        #  'mer_description': 'a little mouse',
        #  'mer_price': 20.0,
        #  'class1_id': 1,
        #  'class2_id': 1,
        #  'fineness_id': 1,
        #  'deliver_price': 10.0,
        #  'send_address_id': addr_id,
        #  'allow_face_trade': True,
        #  'QR_Code': fp
        #  })
        cls.foo2 = Address.objects.create(
            user_name='lhz',
            user_addr='15',
            region=1,
            addr_type=2,
            user_phone=15941121285,
            user=cls.foo
        )
        cls.foo3 = Address.objects.create(
            user_name='lhz1',
            user_addr='15',
            region=1,
            addr_type=1,
            user_phone=15941121285,
            user=cls.foo
        )
        with open('user/1.jpg', 'rb') as fp:
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
            cls.foo4 = Merchandise.objects.create(
                name='xiaomi',
                description='a little phone',
                price=20.0,
                class_level_1_id=1,
                class_level_2_id=1,
                deliver_price=10.0,
                sender_addr=cls.foo2,
                allow_face_trade=True,
                image1=thumb_img,
                thumb=thumb_img,
                upload_user=cls.foo,
            )
    def test_post_transaction(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        signer = TimestampSigner()
        mer_id = signer.sign_object(0)
        rec_address_id = signer.sign_object(1)
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'ZJLYYDS', 'password': '123456'})
        reponse1 = self.client.post('/api/transaction/post_transaction/',
                                    {'mer_id': mer_id, 'rec_address_id': rec_address_id})
        self.assertEqual(reponse1.json()['status'], '400')

    def test_virtual_post(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        signer = TimestampSigner()
        mer_id = signer.sign_object(0)
        rec_address_id = signer.sign_object(1)
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'ZJLYYDS', 'password': '123456'})
        reponse1 = self.client.post('/api/transaction/post_transaction/',
                                    {'mer_id': mer_id, 'rec_address_id': rec_address_id})
        self.assertEqual(reponse1.json()['status'], '400')
        reponse2 = self.client.post('/api/transaction/commit_transaction_virtual/',
                                    {'mer_id': mer_id})
        self.assertEqual(reponse2.json()['status'], '400')



    def test_already_send_transaction(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        signer = TimestampSigner()
        mer_id = signer.sign_object(0)
        rec_address_id = signer.sign_object(1)
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'ZJLYYDS', 'password': '123456'})
        reponse1 = self.client.post('/api/transaction/post_transaction/',
                                    {'mer_id': mer_id, 'rec_address_id': rec_address_id})
        self.assertEqual(reponse1.json()['status'], '400')
        reponse2 = self.client.post('/api/transaction/commit_transaction_virtual/',
                                    {'mer_id': mer_id})
        self.assertEqual(reponse2.json()['status'], '400')
        reponse2 = self.client.post('/api/transaction/already_send_transaction/',
                                    {'current_tra_id': mer_id})
        self.assertEqual(reponse2.json()['status'], '400')


    def test_already_receive_transaction(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        signer = TimestampSigner()
        mer_id = signer.sign_object(0)
        rec_address_id = signer.sign_object(1)
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'ZJLYYDS', 'password': '123456'})
        reponse1 = self.client.post('/api/transaction/post_transaction/',
                                    {'mer_id': mer_id, 'rec_address_id': rec_address_id})
        self.assertEqual(reponse1.json()['status'], '400')
        reponse2 = self.client.post('/api/transaction/commit_transaction_virtual/',
                                    {'mer_id': mer_id})
        self.assertEqual(reponse2.json()['status'], '400')
        reponse3 = self.client.post('/api/transaction/already_send_transaction/',
                                    {'current_tra_id': mer_id})
        self.assertEqual(reponse3.json()['status'], '400')
        reponse4 = self.client.post('/api/transaction/already_receive_transaction/',
                                    {'current_tra_id': mer_id})
        self.assertEqual(reponse3.json()['status'], '400')


    def test_comment_transaction(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        signer = TimestampSigner()
        mer_id = signer.sign_object(0)
        rec_address_id = signer.sign_object(1)
        reponse0 = self.client.post('/api/login0/pc_login/', {'user_email': 'ZJLYYDS', 'password': '123456'})
        reponse1 = self.client.post('/api/transaction/post_transaction/',
                                    {'mer_id': mer_id, 'rec_address_id': rec_address_id})
        self.assertEqual(reponse1.json()['status'], '400')
        reponse2 = self.client.post('/api/transaction/commit_transaction_virtual/',
                                    {'mer_id': mer_id})
        self.assertEqual(reponse2.json()['status'], '400')
        reponse3 = self.client.post('/api/transaction/already_send_transaction/',
                                    {'current_tra_id': mer_id})
        self.assertEqual(reponse3.json()['status'], '400')
        reponse4 = self.client.post('/api/transaction/already_receive_transaction/',
                                    {'current_tra_id': mer_id})
        self.assertEqual(reponse3.json()['status'], '400')
        reponse5 = self.client.post('/api/transaction/comment_transaction/',
                                    {'current_tra_id': mer_id})
        self.assertEqual(reponse3.json()['status'], '400')









