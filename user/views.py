import re

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.shortcuts import render
# from login.tasks import send_active_email
from user.models import ADDR_LOCATION_KEY

from Final_Project1.celery import send_active_email
# Create your views here.
# login/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpRequest
import hashlib
import django.utils.timezone
import commodity.models
import user.models
from order.models import Transaction, TransactionProblem
from utils.get_user_selling import get_user_selling
from .createCaptcha import *
from utils import myemail_sender, random_utils
from Final_Project1.decotators.login_required import login_required
from django.db import transaction
from chat.utils import *
import re
from utils.check_args_valid import *
from Final_Project1.settings import FILE_URL


def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

'''
user_email
password
'''

def has_login_query(request):
    if request.method == 'POST':
        if request.session.get('is_login', False):
            return JsonResponse({
                'status': '200',
                'message': '已登录'
            })
    return HttpResponse(status=407)


def login_fuc(request):
    if request.method == 'POST':
        if request.session.get('is_login', False):
            current_user = user.models.User.objects.get(id=request.session.get('user_id'))
            signer = TimestampSigner()
            return JsonResponse({
                'status': '300',
                'message': '重复登录',
                'user_id': signer.sign_object(current_user.id),
                'user_status': current_user.user_status,
            })
        user_email_name = request.POST.get('user_email', None)
        password = request.POST.get('password', None)
        if not all((user_email_name, password)):
            return JsonResponse({
                'status': '400',
                'message': 'POST字段不全'
            })
        try:
            users = user.models.User.objects.filter(email__exact=user_email_name)
            if not users:
                users = user.models.User.objects.filter(name__exact=user_email_name)
                if not user:
                    return JsonResponse({
                        'status': '402',
                        'message': 'User not exist {}'.format(user_email_name)
                    })
            current_user = users[0]
            if current_user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = current_user.id
                request.session['user_name'] = current_user.name
                signer = TimestampSigner()
                return_message = {
                    'status': '200',
                    'message': "用户 {} 登陆成功".format(current_user.name),
                    'user_id': signer.sign_object(current_user.id),
                    'user_status': current_user.user_status
                }
                response0 = JsonResponse(data=return_message, status=200)
                return response0
            else:
                return JsonResponse({
                    'status': '401',
                    'message': '密码不正确'
                })
        except:
            return JsonResponse({
                'status': '402',
                'message': 'User not exist {}'.format(user_email_name)
            })
    return HttpResponse("Wrong request in {}".format(request.method), status=200)


'''
status
username
password
user_email

'''
def register(request):
    if request.method == 'POST':
        if request.session.get('is_login', False):
            return JsonResponse({
                'status': '300',
                'message': 'User already login {}'.format(request.session.get('user_name', 'unknown_name'))
            })
        if request.POST.get("status") == '0':
            user_email = request.POST.get('user_email')
            code = random_utils.random_str(6, 'upper_str')
            if myemail_sender.mail(user_email, code):
                request.session['code'] = code
                return JsonResponse({
                    'status': '201',
                    'message': '邮件发送成功'
                })
            else:
                return JsonResponse({
                    'status': '401',
                    'message': '邮件发送失败，请检查邮箱地址'
                })
        if request.POST.get("status") == '1':
            try:
                code = request.session['code']
            except:
                message = 'cookie 错误'
                request.session.flush()
                return JsonResponse({'message': message, 'status': '410'})
            if not request.POST.get('code') == code:
                return JsonResponse({
                    'status': '402',
                    'message': '验证码错误'
                })
            else:
                username = request.POST.get('username', None)
                password = request.POST.get('password', None)
                email = request.POST.get('user_email', None)
                if not all((email, username, password)):
                    message = 'email username password 不能为空'
                    request.session.flush()
                    return JsonResponse({'message': message, 'status': '510'})
                if not check_args_valid([username, password, email]):
                    return JsonResponse({
                        'status': '400',
                        'message': 'POST字段错误'
                    })
                same_name_user = user.models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    return JsonResponse({
                        'status': '404',
                        'message': '用户已经存在，请重新选择用户名！'
                    })
                same_email_user = user.models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    return JsonResponse({
                        'status': '404',
                        'message': '该邮箱地址已被注册，请使用别的邮箱！'
                    })
                new_user = user.models.User.objects.create()
                new_user.name = username
                new_user.password = hash_code(password)  # 使用加密密码
                new_user.email = email
                new_user.save()
                return JsonResponse({
                        'status': '200',
                        'message': '用户{}注册成功'.format(username)
                    })
    return HttpResponse(status=500)

'''
status
'''
def new_register_email(request):
    if request.method == 'POST':
        key = 'ip_{}_send_email'.format(request.META['REMOTE_ADDR'])
        conn = get_redis_connection('default')
        if request.session.get('is_login', False):
            return JsonResponse({
                'status': '300',
                'message': 'User already login {}'.format(request.session.get('user_name', 'unknown_name'))
            })
        if request.POST.get("status") == '0':
            has_send = conn.get(key)
            if has_send:
                return JsonResponse({
                    'status': '407',
                    'message': '60s内重复发送邮件'
                })
            else:
                conn.set(key, 1, 50)
            user_email = request.POST.get('user_email')
            if not user_email:
                return JsonResponse({
                    'status': '400',
                    'message': 'POST字段不全'
                }, status=200)
            if re.match(r'[0-9_]{0,19}@mail.sustech.edu.cn', user_email) or re.match(r'[0-9a-zA-Z_]{0,19}@qq.com',
                                                                               user_email) or re.match(
                    r'[0-9a-zA-Z_]{0,19}@163.com', user_email) or re.match(r'[0-9a-zA-Z_]{0,19}@sustech.edu.cn', user_email):
                pass
            else:
                return JsonResponse({
                    'status': '500',
                    'message': '邮箱地址格式错误'
                })
            code = random_utils.random_str(6, 'upper_str')
            send_active_email.delay(code=code, email=user_email, current_user_name='新注册用户',
                                    img_url='', price='', rela_mer='', type=1)
            request.session['code'] = code
            return JsonResponse({
                    'status': '200',
                    'message': '邮件发送成功'
                })
    return HttpResponse(status=500)


@login_required()
def logout(request):
    request.session.flush()
    return HttpResponse(status=200)


def mobile_login(request):
    if request.method == 'POST':
        if request.session.get('is_login', False):
            return JsonResponse(status=300)
        user_email_name = request.POST.get('user_email', '')
        password = request.POST.get('password', '')
        signer = TimestampSigner()
        try:
            users = user.models.User.objects.filter(email__exact=user_email_name)
            if not users:
                users = user.models.User.objects.filter(name__exact=user_email_name)
                if not users:
                    return JsonResponse({
                        'status': '402',
                        'message': 'User not exist {}'.format(user_email_name)
                    })
            current_user = users[0]
            if current_user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = current_user.id
                request.session['user_name'] = current_user.name
                return_message = {
                    'status': '200',
                    'message': "用户 {} 登陆成功".format(current_user.name),
                    'user_status': current_user.user_status,
                    'user_id': signer.sign_object(current_user.id)
                }
                response0 = JsonResponse(data=return_message,  status=200)
                return response0
            else:
                return JsonResponse({
                    'status': '401',
                    'message': '密码不正确'
                })
        except:
            response = HttpResponse(status=200)
            response.headers['message'] = 'User not exist {}, {}'.format(user_email_name, password)
            return JsonResponse({
                'status': '402',
                'message': 'User not exist {}'.format(user_email_name)
            })
    return HttpResponse(status=500)


@login_required(status=2)
def upload_commodity(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    mer_name = request.POST.get('mer_name', None)
    mer_description = request.POST.get('mer_description', None)
    mer_price = request.POST.get('mer_price', None)
    class1_id = request.POST.get('class1_id', None)
    class2_id = request.POST.get('class2_id', None)
    fineness_id = request.POST.get('fineness_id', None)
    deliver_price = request.POST.get('deliver_price', None)
    send_address_id = request.POST.get('send_address_id', None)
    allow_face_trade = request.POST.get('allow_face_trade', True)
    signer = TimestampSigner()
    try:
        image1 = request.FILES['image1']
    except:
        return JsonResponse({
            'status': '201',
            'message': '用户未上传图片'
        }, status=200)
    if not all((mer_name, mer_description, mer_price, class1_id, class2_id, fineness_id, deliver_price)):
        return JsonResponse({
            'status': '201',
            'message': '有未填字段请检查'
        }, status=200)
    if not send_address_id:
        return JsonResponse({
            'status': '400',
            'message': '请完善发货地址',
        }, status=200)
    else:
        send_address_id = signer.unsign_object(send_address_id)
        try:
            sender_addr = user.models.Address.objects.filter(addr_type=2).get(id=send_address_id)
        except:
            return JsonResponse({
                'status': '400',
                'message': '地址id错误',
            }, status=200)
    if not check_args_valid([mer_name, mer_description, mer_price, class1_id, class2_id, fineness_id, deliver_price]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    if re.match('^[-+]?[0-9]+(\.[0-9]{1,2})?$',mer_price) and re.match('^[-+]?[0-9]+(\.[0-9]{1,2})?$', deliver_price):
        pass
    else:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        image2 = request.FILES['image2']
    except:
        image2 = None
    try:
        image3 = request.FILES['image3']
    except:
        image3 = None
    # try:

    new_merchandise = commodity.models.Merchandise.objects.create(
        name=mer_name,
        description=mer_description,
        price=mer_price,
        upload_user=current_user,
        class_level_1_id=class1_id,
        class_level_2_id=class2_id,
        fineness=fineness_id,
        sender_addr=sender_addr,
        deliver_price=deliver_price,
        allow_face_trade=allow_face_trade,
        )
    # except:
    #     return JsonResponse({
    #         'status': '600',
    #         'message': '重复或键值错误'
    #     }, status=200)
    reopen_img1 = Image.open(image1)
    reopen_img1.thumbnail((200, 100), Image.ANTIALIAS)
    buffer = BytesIO()
    reopen_img1.save(buffer, format='PNG')#file, field_name, name, content_type, size, charset, content_type_extra=None
    thumb_img = InMemoryUploadedFile(
        file = buffer,
        field_name='thumb',
        name="thumb.png",
        content_type='image/jpeg',
        size=buffer.tell(),
        charset=None
    )
    new_merchandise.image1 = image1
    new_merchandise.image2 = image2
    new_merchandise.image3 = image3
    new_merchandise.thumb = thumb_img
    new_merchandise.save()
    sender_addr.relate_number = sender_addr.relate_number + 1
    sender_addr.save()
    current_user.uploaded_goods_numbers += 1
    current_user.save()
    send_notice(current_user.id, "商品{}上传成功".format(new_merchandise.name), current_user=current_user, rela_mer=new_merchandise)
    return JsonResponse({
        'status': '200',
        'message': '商品：{}, 用户:{} 上传成功'.format(str(new_merchandise), str(current_user))
    }, status=200)


@transaction.atomic()
@login_required(status=2)
def delete_commodity(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    mer_id = request.POST.get('mer_id', None)
    signer = TimestampSigner()
    if not mer_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([mer_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        mer_id = signer.unsign_object(mer_id)
        current_mer = commodity.models.Merchandise.objects.get(id=mer_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id错误',
        }, status=200)
    if current_mer.status != 1:
        return JsonResponse({
            'status': '400',
            'message': '商品状态异常',
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_mer.status = 0
        current_mer.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, "商品{}下架成功".format(current_mer.name), current_user=current_user, rela_mer=current_mer)
    return JsonResponse({
        'status': '200',
        'message': "商品{}下架成功".format(current_mer.name)
    }, status=200)


@login_required(status=1)
def wait_payment_fuc(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    all_user_transaction_wait_payment = Transaction.objects.filter(
        transaction_receiver=current_user).filter(status__exact=1)
    transaction_list = []
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    for i in all_user_transaction_wait_payment.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_wait_payment.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_deliver_fuc(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_wait_deliver = Transaction.objects.filter(
        transaction_receiver=current_user).filter(status__exact=2)
    transaction_list = []
    for i in all_user_transaction_wait_deliver.all():
        transaction_list.append(i.get_simple_overview())
    return_list_len = len(transaction_list)
    if return_list_len > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_receiving_fuc(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_wait_receiving = Transaction.objects.filter(
        transaction_receiver=current_user).filter(status__exact=3)
    transaction_list = []
    for i in all_user_transaction_wait_receiving.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_wait_receiving.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_comment_fuc(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_success = Transaction.objects.filter(transaction_receiver=current_user).filter(status__exact=4)
    transaction_list = []
    for i in all_user_transaction_success.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_success.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def success_fuc(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_success = Transaction.objects.filter(transaction_receiver=current_user).filter(status__exact=5)
    transaction_list = []
    for i in all_user_transaction_success.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_success.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_payment_fuc_seller(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_wait_payment = Transaction.objects.filter(
        transaction_sender=current_user).filter(status__exact=1)
    transaction_list = []
    for i in all_user_transaction_wait_payment.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_wait_payment.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_deliver_fuc_seller(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_wait_deliver = Transaction.objects.filter(
        transaction_sender=current_user).filter(status__exact=2)
    transaction_list = []
    for i in all_user_transaction_wait_deliver.all():
        transaction_list.append(i.get_simple_overview())
    return_list_len = len(transaction_list)
    if return_list_len > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_receiving_fuc_seller(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_wait_receiving = Transaction.objects.filter(
        transaction_sender=current_user).filter(status__exact=3)
    transaction_list = []
    for i in all_user_transaction_wait_receiving.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_wait_receiving.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def wait_comment_fuc_seller(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_success = Transaction.objects.filter(transaction_sender=current_user).filter(status__exact=4)
    transaction_list = []
    for i in all_user_transaction_success.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_success.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def success_fuc_seller(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    all_user_transaction_success = Transaction.objects.filter(transaction_sender=current_user).filter(status__exact=5)
    transaction_list = []
    for i in all_user_transaction_success.all():
        transaction_list.append(i.get_simple_overview())
    if all_user_transaction_success.count() > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': transaction_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


file_url = FILE_URL


@login_required()
def all_user_selling_merchandise(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    return_list = get_user_selling(current_user.id)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    merchandises_count = len(return_list)
    if merchandises_count > end_position:
        has_next = True
    else:
        has_next = False
    if merchandises_count == 0:
        is_empty = True
    else:
        is_empty = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_merchandise': return_list[start_position:end_position],
        'has_next': str(has_next),
        'is_empty': str(is_empty)
    }, status=200)


@login_required()
def all_user_upload_merchandise(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    selling_List = commodity.models.Merchandise.objects.filter(
        upload_user_id__exact=current_user.id).filter(status__exact=1)
    return_list = []
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    for i in selling_List.all():
        return_list.append(i.get_simple_info())
    merchandises_count = len(return_list)
    if merchandises_count > end_position:
        has_next = True
    else:
        has_next = False
    if merchandises_count == 0:
        is_empty = True
    else:
        is_empty = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_merchandise': return_list[start_position:end_position],
        'has_next': str(has_next),
        'is_empty': str(is_empty)
    }, status=200)


@login_required()
def all_user_favorite_merchandise(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    favorite_merchandise_list = current_user.favorite_merchandise
    favorite_merchandise_data_list = []
    try:
        for i in favorite_merchandise_list:
            favorite_merchandise_data_list.append(commodity.models.Merchandise.objects.get(id=i).get_simple_info())
    except:
        return JsonResponse({
            'status': '300',
            'message': '数据库列表id错误'
        }, status=200)

    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    return_len = len(favorite_merchandise_data_list)
    if return_len > end_position:
        has_next = True
    else:
        has_next = False
    if return_len == 0:
        is_empty = True
    else:
        is_empty = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_info': favorite_merchandise_data_list[min(start_position, return_len):min(end_position, return_len)],
        'has_next': str(has_next),
        'is_empty': str(is_empty)
    }, status=200)


@login_required()
def all_user_favorite_business(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    favorite_business_list = current_user.favorite_sellers
    favorite_business_data_list = []
    try:
        for i in favorite_business_list:
            current_business = user.models.User.objects.get(id=i)
            favorite_business_data_list.append(current_business.get_simple_info())
    except:
        return JsonResponse({
            'status': '300',
            'message': '数据库列表id错误'
        }, status=200)

    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    return_len = len(favorite_business_data_list)
    if return_len > end_position:
        has_next = True
    else:
        has_next = False
    if return_len == 0:
        is_empty = True
    else:
        is_empty = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_info': favorite_business_data_list[
                       min(start_position, return_len):min(end_position, return_len)],
        'has_next': str(has_next),
        'is_empty': str(is_empty)
    }, status=200)


@login_required(status=1)
def add_address(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    user_name = request.POST.get('user_name', None)
    user_addr = request.POST.get('user_addr', None)
    user_phone = request.POST.get('user_phone', None)
    region_id = request.POST.get('region_id', None)
    address_type = int(request.POST.get("address_type", 1))
    is_default = request.POST.get('is_default', False)
    longitude = request.POST.get('longitude', None)
    latitude = request.POST.get('latitude', None)
    if address_type != 1:
        if current_user.user_status != 2:
            return JsonResponse({
                'status': '401',
                'message': '不是卖家不能上传发货地址'
            }, status=200)
    if not all((user_name, user_addr, user_phone, region_id)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全'
        }, status=200)

    if not check_args_valid([user_name, user_addr, user_phone, region_id]):
        return JsonResponse({
            'status': '401',
            'message': 'POST字段错误'
        })
    try:
        region_id = int(region_id)
        sys_longitude = ADDR_LOCATION_KEY[region_id][0]
        sys_latitude = ADDR_LOCATION_KEY[region_id][1]
    except:
        return JsonResponse({
            'status': '402',
            'message': 'POST字段错误'
        })
    try:
        if longitude and latitude:
            longitude = float(longitude)
            latitude = float(latitude)
        else:
            longitude = sys_longitude
            latitude = sys_latitude
    except:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })

    # try:
    new_addr = user.models.Address.objects.create(
        user_name=user_name,
        user_addr=user_addr,
        user_phone=user_phone,
        user=current_user,
        is_default=is_default,
        region=region_id,
        addr_type=address_type,
        latitude=latitude,
        longitude=longitude,
    )
    new_addr.save()
    return JsonResponse({
        'status': '200',
        'message': '成功'
    }, status=200)
    # except:
    #     return JsonResponse({
    #         'status': '400',
    #         'message': '创建失败'
    #     }, status=200)


@login_required(status=1)
def delete_address(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    addr_id = request.POST.get('addr_id', None)
    if not addr_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全'
        }, status=200)
    if not check_args_valid([addr_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        signer = TimestampSigner()
        addr_id = signer.unsign_object(addr_id)
        current_addr = user.models.Address.objects.get(id=addr_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id错误'
        }, status=200)
    # try:
    mer_list = commodity.models.Merchandise.objects.filter(status__gt=0).filter(sender_addr=current_addr).all()
    return_mer_list = []
    if len(mer_list) > 0:
        for mer in mer_list:
            return_mer_list.append(mer.get_simple_info())
        return JsonResponse({
            'status': '400',
            'message': '关联mer',
            'return_mer_list': return_mer_list
        }, status=200)
    current_addr.delete()
    return JsonResponse({
        'status': '200',
        'message': '成功'
    }, status=200)


@login_required(status=1)
def get_address_list(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
        addr_list = user.models.Address.objects.filter(user=current_user).all()
        return_list = []
        for i in addr_list:
            return_list.append(i.get_info())
        return_len = len(return_list)
        if return_len > end_position:
            has_next = True
        else:
            has_next = False
        if return_len == 0:
            is_empty = True
        else:
            is_empty = False
        return JsonResponse({
            'status': '200',
            'message': '查询成功',
            'return_list': return_list[start_position:end_position],
            'has_next': has_next,
            'is_empty': is_empty,
        }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '系统错误'
        }, status=200)


@login_required()
def upload_head_photo(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    header_photo = request.FILES.get('header_photo', None)
    if not header_photo:
        return JsonResponse({
            'status': '201',
            'message': '用户未上传图片'
        }, status=504)
    try:
        current_user.header_photo = header_photo
        current_user.has_header_photo = True
        current_user.save()
        return JsonResponse({
            'status': '200',
            'message': '头像更改成功'
        }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '更改失败'
        }, status=500)


@transaction.atomic
@login_required()
def activate(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    real_name = request.POST.get('real_name', None)
    user_identify = request.POST.get('user_identify', None)
    self_description = request.POST.get('self_description', None)
    # addr_id = request.POST.get("addr_id", None)
    pay_password = request.POST.get('pay_password', None)
    if current_user.user_status != 0:
        return JsonResponse({
            'status': '400',
            'message': '用户状态错误'
        }, status=200)
    if not all((real_name, user_identify, pay_password)):
        return JsonResponse({
            'status': '400',
            'message': '用户上传字段不全'
        }, status=200)
    if not check_args_valid([real_name, user_identify, pay_password]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    sid = transaction.savepoint()
    # try:
    signer = TimestampSigner()
    # addr_id = signer.unsign_object(addr_id)
    # cur_addr = user.models.Address.objects.filter(id__exact=addr_id)
    # if not cur_addr:
    #     return JsonResponse({
    #     'status': '400',
    #     'message': '用户没有地址'
    # }, status=200)
    # if cur_addr.all()[0].addr_type == 2:
    #     return JsonResponse({
    #         'status': '400',
    #         'message': '地址类型错误'
    #     }, status=200)
    current_user.real_name = real_name
    current_user.user_identify = user_identify
    current_user.self_description = self_description
    current_user.user_status = 1
    current_user.pay_password = hash_code(pay_password)
    # cur_addr.is_default = True
    # cur_addr.save()
    current_user.save()
    # except:
    #     transaction.savepoint_rollback(sid)
    #     return JsonResponse({
    #         'status': '400',
    #         'message': '更改失败'
    #     }, status=500)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id,
                "修改详细资料成功， 现在可以开始购买了", current_user=current_user)
    return JsonResponse({
        'status': '200',
        'message': '激活成功'
    }, status=200)


@login_required(status=1)
def modify_self_info(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    real_name = request.POST.get('real_name', None)
    user_identify = request.POST.get('user_identify', None)
    self_description = request.POST.get('self_description', None)
    if not all((real_name, user_identify, self_description)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    if not check_args_valid([real_name, user_identify, self_description]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        if current_user:
            current_user.real_name = real_name
        if user_identify:
            current_user.user_identify = user_identify
        if self_description:
            current_user.self_description = self_description
        current_user.save()
        return JsonResponse({
            'status': '200',
            'message': '激活成功'
        }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '更改失败'
        }, status=200)


@login_required(status=1)
def get_user_details(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    try:
        return JsonResponse({
            'status': '200',
            'message': '查询成功',
            'user_details': current_user.get_simple_info()
        }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '查询失败'
        }, status=200)


@transaction.atomic
@login_required(status=1)
def upload_QR_Code(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    # addr_id = request.POST.get("addr_id", None)
    if current_user.user_status != 1:
        return JsonResponse({
            'status': '400',
            'message': '用户状态错误'
        }, status=200)
    # if not addr_id:
    #     return JsonResponse({
    #         'status': '400',
    #         'message': 'POST字段不全'
    #     }, status=200)
    signer = TimestampSigner()
    # addr_id = signer.unsign_object(addr_id)
    # cur_addr = user.models.Address.objects.filter(id__exact=addr_id)
    # if not cur_addr:
    #     return JsonResponse({
    #     'status': '400',
    #     'message': '用户没有地址'
    # }, status=200)
    # if cur_addr.all()[0].addr_type == 1:
    #     return JsonResponse({
    #         'status': '400',
    #         'message': '地址类型错误'
    #     }, status=200)
    try:
        current_QR_Code = request.FILES['QR_Code']
    except:
        return JsonResponse({
            'status': '201',
            'message': '用户未上传图片'
        }, status=200)
    if current_user.user_status !=1:
        return JsonResponse({
            'status': '400',
            'message': '用户状态错误'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_user.money_receiving_QR_code = current_QR_Code
        current_user.user_status = 2
        current_user.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '更改失败'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id,
                "上传付款码成功， 现在可以上传商品了", current_user=current_user)
    return JsonResponse({
        'status': '200',
        'message': '激活成功'
    }, status=200)


@login_required(status=1)
def get_QR_Code(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    user_id = request.POST.get('user_id', None)
    signer = TimestampSigner()
    try:
        user_id = signer.unsign_object(user_id)
        uploader = user.models.User.objects.get(id=user_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id错误'
        }, status=200)
    QR_code_url = f"{file_url}{signer.sign_object(uploader.get_QRCode_info())}",
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'QR_code_url':QR_code_url,
    }, status=200)


@login_required(status=1)
def user_page(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    user_id = request.POST.get('user_id', None)
    if not user_id:
        return JsonResponse({
        'status': '400',
        'message': 'id错误'
    }, status=200)
    try:
        signer = TimestampSigner()
        user_id = signer.unsign_object(user_id)
        target_uesr = user.models.User.objects.get(id=user_id)
        base_info = target_uesr.get_base_info()
        selling_List_ord = commodity.models.Merchandise.objects.filter(upload_user_id__exact=user_id).filter(
            status__exact=1)
        selling_list = []
        for i in selling_List_ord.all():
            selling_list.append(i.get_simple_info())
        return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'base_info': base_info,
        'selling_list': selling_list
    }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '查询错误'
        }, status=200)


@login_required(status=1)
def add_cart(request:HttpRequest) -> JsonResponse:
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    mer_id = request.POST.get('mer_id', None)
    if not mer_id:
        return JsonResponse({
        'status': '400',
        'message': 'POST字段不全'
    }, status=200)
    try:
        signer =TimestampSigner()
        mer_id = signer.unsign_object(mer_id)
        current_mer = commodity.models.Merchandise.objects.get(id=mer_id)
        if current_mer.upload_user == current_user:
            return JsonResponse({
                'status': '400',
                'message': '不能添加自己的商品进购物车'
            }, status=200)
        conn = get_redis_connection('default')
        key = "cart_{}".format(current_user.id)
        conn.hset(key, mer_id, 1)
        return JsonResponse(
            {
                'status': '200',
                'message': '添加成功',
            }
        , status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '添加错误'
        }, status=200)


@login_required(status=1)
def cart_count(request:HttpRequest) -> JsonResponse:
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    conn = get_redis_connection('default')
    cart_key = 'cart_{}'.format(current_user.id)
    res = 0
    res_list = conn.hvals(cart_key)
    for i in res_list:
        res += int(i)
    # 返回结果
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'count': res
    }, status=200)


@login_required(status=1)
def cart_show(request:HttpRequest) -> JsonResponse:
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    conn = get_redis_connection('default')
    cart_key = 'cart_{}'.format(current_user.id)
    res_dict = conn.hgetall(cart_key)
    return_List = []
    # 保存所有商品的总数
    total_count = 0
    # 保存所有商品的总价格
    total_price = 0

    # 遍历res_dict获取商品的数据
    for id, count in res_dict.items():
        # 根据id获取商品的信息
        current_mer = commodity.models.Merchandise.objects.get(id=id)
        # 保存商品的小计
        info = current_mer.get_simple_info()
        info['amount'] = int(count) * current_mer.price
        # books_li.append((books, count))
        total_count += int(count)
        total_price += int(count) * current_mer.price
        return_List.append(info)
    return JsonResponse({
        'info': return_List,
        'total_count': total_count,
        'total_price': total_price,
        'message': '查询成功'
    }, status=200)


@login_required(status=1)
def cart_del(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    mer_id = request.POST.get('mer_id', None)
    if not mer_id:
        return JsonResponse({
        'status': '400',
        'message': 'POST字段不全'
    }, status=200)
    if not check_args_valid([mer_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    current_mer = commodity.models.Merchandise.objects.filter(id__exact=mer_id)
    if not current_mer:
        return JsonResponse({
            'status': '400',
            'message': '商品不存在'
        }, status=200)
    conn = get_redis_connection('default')
    cart_key = 'cart_{}'.format(current_user.id)
    conn.hdel(cart_key, mer_id)
    return JsonResponse({
        'message': '删除成功'
    }, status=200)


@transaction.atomic
@login_required(status=1)
def recharge(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    money_num = request.POST.get("money", None)
    if not money_num:
        return JsonResponse({
        'status': '400',
        'message': 'POST字段不全'
    }, status=200)
    if not re.match('^[-+]?[0-9]+(\.[0-9]{1,2})?$', money_num) :
        return JsonResponse({
            'status': '400',
            'message': 'POST字段非法'
        }, status=200)
    if not check_args_valid([money_num]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        money_num = float(money_num)
    except:
        return JsonResponse({
            'status': '500',
            'message': '充值钱数不正确'
        }, status=200)
    if money_num <= 0:
        return JsonResponse({
            'status': '500',
            'message': '充值钱数不能为负'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_user.money = current_user.money + money_num
        current_user.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    return JsonResponse({
        'status': '200',
        'message': '充值成功'
    }, status=200)


@login_required()
def get_notification_list(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    notification_list = current_user.notice_info_unread
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    end_position = max(len(notification_list) + 10, end_position)
    return_list = []
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    for rec in notification_list:
        return_list.append(rec)
        current_user.notice_info.append(rec)
    try:
        current_user.save()
    except:
        return JsonResponse({
            'status': '400',
            'message': '系统错误',
        }, status=200)
    notice_info_list = current_user.notice_info
    notice_info_list.sort(key=lambda x: x["date"])
    notice_info_list.reverse()
    notification_list.reverse()
    current_user.notice_info_unread = []
    current_user.save()
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'notification_list': notification_list,
        'notice_list': notice_info_list[start_position:end_position],
    }, status=200)


@transaction.atomic
@login_required()
def change_password(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    old_password = request.POST.get('old_password', None)
    new_password = request.POST.get('new_password', None)
    if not all((old_password, new_password)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全'
        }, status=200)
    if not check_args_valid([old_password, new_password]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    if hash_code(old_password) != current_user.password:
        return JsonResponse({
            'status': '300',
            'message': '原密码错误'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_user.password = hash_code(new_password)
        current_user.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '500',
            'message': '系统错误'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '修改密码成功', current_user=current_user)
    return JsonResponse({
        'status': '200',
        'message': '修改成功'
    }, status=200)


@transaction.atomic
@login_required(status=1)
def change_pay_password(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    old_pay_password = request.POST.get('old_pay_password', None)
    new_pay_password = request.POST.get('new_pay_password', None)
    if not all((old_pay_password, new_pay_password)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全'
        }, status=200)
    if not check_args_valid([old_pay_password, new_pay_password]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    if hash_code(old_pay_password) != current_user.pay_password:
        return JsonResponse({
            'status': '300',
            'message': '原密码错误'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_user.pay_password = hash_code(new_pay_password)
        current_user.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '500',
            'message': '系统错误'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '修改支付密码成功', current_user=current_user)
    return JsonResponse({
        'status': '200',
        'message': '修改成功'
    }, status=200)


@login_required()
def get_all_comments(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    target_user_id = request.POST.get('target_user_id', None)
    if not target_user_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全'
        }, status=200)
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    signer = TimestampSigner()
    try:
        start_position = int(start_position)
        end_position = int(end_position)
        target_user_id = signer.unsign_object(target_user_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'position异常',
        }, status=200)
    comments_list = user.models.Comment.objects.filter(comment_target__id__exact=target_user_id).all()
    return_list = []
    for com in comments_list:
        return_list.append(com.get_detail_info())
    return_len = len(return_list)
    has_next = False
    if return_len >= end_position:
        has_next = True
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'return_List': return_list[start_position:end_position],
        'has_next': has_next,
    }, status=200)


#推荐
@login_required()
def get_recommend_list(request):
    mer_list = commodity.models.Merchandise.objects.filter(status=1).all()
    if len(mer_list) < 10:
        return JsonResponse({
            'status': '400',
            'message': '商品数不足',
        }, status=200)
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    key = "recommend_list"
    conn = get_redis_connection('default')
    recommend_list = conn.get(key)
    recommend_list = literal_eval(recommend_list)
    user_recommend_list = current_user.user_recommend_list
    return_id_list = []
    for mer_id in user_recommend_list:
        return_id_list.append(mer_id)
    for mer_id in recommend_list:
        if len(return_id_list) < 15:
            return_id_list.append(mer_id)
    if len(return_id_list) < 15:
        mer_list = commodity.models.Merchandise.objects.all()
        for mer in mer_list:
            if len(return_id_list) < 15:
                if mer.id not in return_id_list:
                    return_id_list.append(mer.id)
            else:
                break
    return_list = []
    for id in return_id_list:
        try:
            current_mer = commodity.models.Merchandise.objects.get(id=id)
            if current_mer.status == 1:
                return_list.append(current_mer.get_simple_info())
        except:
            continue

    return JsonResponse({
        'status': '200',
        'message': '成功',
        'return_List': return_list,
    }, status=200)


@login_required(status=1)
def get_problem_list(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段异常',
        }, status=200)
    problem_list = TransactionProblem.objects.filter(problem_user=current_user).all()
    return_list = []
    for pro in problem_list:
        return_list.append(pro.get_detail_info())
    has_next = False
    if len(return_list) > end_position:
        has_next = True
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'return_List': return_list[start_position:end_position],
        'has_next': has_next
    }, status=200)


def forget_password_email(request):
    if request.method == 'POST':
        key = 'ip_{}_send_forget_email'.format(request.META['REMOTE_ADDR'])
        conn = get_redis_connection('default')
        has_send = conn.get(key)
        if has_send:
            return JsonResponse({
                'status': '407',
                'message': '60s内重复发送邮件'
            }, status=200)
        else:
            conn.set(key, 1, 50)
        if request.session.get('is_login', False):
            return JsonResponse({
                'status': '300',
                'message': 'User already login {}'.format(request.session.get('user_name', 'unknown_name'))
            }, status=200)
        user_email = request.POST.get('user_email', None)
        if not user_email:
            return JsonResponse({
                'status': '407',
                'message': 'post字段不全'
            }, status=200)
        if re.match(r'[0-9_]{0,19}@mail.sustech.edu.cn', user_email) or re.match(r'[0-9a-zA-Z_]{0,19}@qq.com',
                                                                                 user_email) or re.match(
            r'[0-9a-zA-Z_]{0,19}@163.com', user_email) or re.match(r'[0-9a-zA-Z_]{0,19}@sustech.edu.cn', user_email):
            pass
        else:
            return JsonResponse({
                'status': '500',
                'message': '邮箱地址格式错误'
            })
        current_user = user.models.User.objects.filter(email__exact=user_email)
        if not current_user:
            return JsonResponse({
                'status': '400',
                'message': '邮箱对应用户不存在'
            })
        current_user = current_user.all()[0]
        code = random_utils.random_str(6, 'upper_str')
        # send_active_email.delay(code=code, email=user_email, current_user=None, type=3)
        send_active_email.delay(code=code, email=user_email, current_user_name=current_user.name,
                                img_url='', price='', rela_mer='', type=3)
        request.session['forget_code'] = code
        request.session['forget_email'] = user_email
        return JsonResponse({
            'status': '200',
            'message': '邮件发送成功'
        }, status=200)
    return HttpResponse(status=500)


def forget_password(request):
    if request.method == 'POST':
        try:
            code = request.session['forget_code']
        except:
            return JsonResponse({
                'status': '400',
                'message': 'session错误'
            }, status=200)
        post_code = request.POST.get('post_code', None)
        new_password = request.POST.get('new_password', None)
        if not all((new_password, post_code)):
            return JsonResponse({
                'status': '400',
                'message': 'POST字段不全'
            }, status=200)
        if not check_args_valid([new_password, post_code]):
            return JsonResponse({
                'status': '400',
                'message': 'POST字段错误'
            })
        if code != post_code:
            return JsonResponse({
                'status': '400',
                'message': 'code错误'
            }, status=200)

        forget_email = request.session['forget_email']
        current_user = user.models.User.objects.filter(email__exact=forget_email)
        if current_user:
            current_user = current_user.all()[0]
        current_user.password = hash_code(new_password)
        current_user.save()
        return JsonResponse({
            'status': '200',
            'message': '成功',
        }, status=200)
    return HttpResponse(status=500)


@login_required(status=1)
def forget_pay_password_email(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    key = 'ip_{}_send_forget_pay_password_email'.format(request.META['REMOTE_ADDR'])
    conn = get_redis_connection('default')
    has_send = conn.get(key)
    if has_send:
        return JsonResponse({
            'status': '407',
            'message': '60s内重复发送邮件'
        }, status=200)
    else:
        conn.set(key, 1, 50)
    user_email = current_user.email
    code = random_utils.random_str(6, 'upper_str')
    send_active_email.delay(code=code, email=user_email, current_user_name=current_user.name,
                            img_url='', price='', rela_mer='', type=3)
    request.session['forget_code'] = code
    request.session['forget_pay_email'] = user_email
    return JsonResponse({
        'status': '200',
        'message': '邮件发送成功'
    }, status=200)


@login_required(status=1)
def forget_pay_password(request):
    if request.method == 'POST':
        try:
            code = request.session['forget_code']
        except:
            return JsonResponse({
                'status': '400',
                'message': 'session错误'
            }, status=200)
        post_code = request.POST.get('post_code', None)
        new_password = request.POST.get('new_password', None)
        if not all((new_password, post_code)):
            return JsonResponse({
                'status': '400',
                'message': 'POST字段不全'
            }, status=200)
        if not check_args_valid([new_password, post_code]):
            return JsonResponse({
                'status': '400',
                'message': 'POST字段错误'
            })
        if code != post_code:
            return JsonResponse({
                'status': '400',
                'message': 'code错误'
            }, status=200)
        forget_email = request.session['forget_pay_email']
        current_user = user.models.User.objects.filter(email__exact=forget_email)
        if current_user:
            current_user = current_user.all()[0]
        current_user.pay_password = hash_code(new_password)
        current_user.save()
        return JsonResponse({
            'status': '200',
            'message': '成功',
        }, status=200)
    return HttpResponse(status=500)


@login_required()
def get_current_user_info(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'info': current_user.get_base_info()
    }, status=200)


@login_required()
def upload_user_position(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    longitude = request.POST.get('longitude', None)
    latitude = request.POST.get('latitude', None)
    if not all((longitude, latitude)):
        JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    try:
        longitude = float(longitude)
        latitude = float(latitude)
    except:
        JsonResponse({
            'status': '400',
            'message': 'POST字段错误',
        }, status=200)
    current_user.longitude = longitude
    current_user.latitude = latitude
    current_user.save()
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)





