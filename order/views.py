import hashlib

from django.http import HttpResponse, JsonResponse, HttpRequest
import django.utils.timezone
import commodity.models
import user.models
from order.models import Transaction, TransactionProblem
from utils import myemail_sender, random_utils
from django.core.signing import TimestampSigner
from Final_Project1.decotators.login_required import login_required
from django.db import transaction
from chat.utils import *
from order.utils import *
from django.db.models import Q
from utils.check_args_valid import *
from Final_Project1.settings import FILE_URL
import utils.random_utils

file_url = FILE_URL

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


@login_required()
def detail_fuc(request):
    signer = TimestampSigner()
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    transaction_id = request.POST.get('transaction_id', None)
    if not transaction_id:
        return JsonResponse({
            'status': '600',
            'message': '未上传transaction_id'
        }, status=200)
    if not check_args_valid([transaction_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        transaction_id = signer.unsign_object(transaction_id)
        current_transaction = Transaction.objects.get(id=transaction_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '传入的transaction_id 不存在',
        }, status=200)
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'transaction_sender_id': signer.sign_object(current_transaction.transaction_sender.id),
        'transaction_sender_name': current_transaction.transaction_sender.name,
        'transaction_receiver_id': signer.sign_object(current_transaction.transaction_receiver.id),
        'transaction_receiver_name': current_transaction.transaction_receiver.name,
        'transaction_merchandise_info': current_transaction.transaction_merchandise.get_simple_info(),
        'transaction_status': current_transaction.status,
        'pay_time': current_transaction.pay_time,
        'receive_time': current_transaction.receive_time,
        'create_time': current_transaction.create_time,
        'sender_location': current_transaction.sender_location,
        'receiver_location': current_transaction.receiver_location,
        'price': current_transaction.price
    }, status=200)


@login_required()
def get_identify_code(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    identify_code = random_utils.random_str(18, 'upper_str')
    return JsonResponse({
                'status': '200',
                'message': '请求成功',
                'identify_code': identify_code
            }, status=200)


@transaction.atomic
@login_required()
def post_transaction(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    mer_id = request.POST.get('mer_id', None)
    identify_code = request.POST.get("identify_code", None)
    if not mer_id:
        return JsonResponse({
            'status': '400',
            'message': '传入的post字段不全',
        }, status=200)
    if not check_args_valid([mer_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    rec_address_id = request.POST.get('rec_address_id', None)
    signer = TimestampSigner()
    if not rec_address_id:
        return JsonResponse({
            'status': '200',
            'message': '请完善收货地址',
        }, status=200)
    else:
        rec_address_id = signer.unsign_object(rec_address_id)
        try:
            rec_addr = user.models.Address.objects.get(id=rec_address_id)
        except:
            return JsonResponse({
                'status': '200',
                'message': '地址id错误',
            }, status=200)
    try:
        mer_id = signer.unsign_object(mer_id)
        current_mer = commodity.models.Merchandise.objects.get(id=mer_id)
        current_sender = current_mer.upload_user
        send_addr = current_mer.sender_addr
        if current_mer.upload_user.id == current_user.id:
            return JsonResponse({
                'status': '400',
                'message': '自己不能买自己发布的商品',
            }, status=200)
        if not send_addr:
            return JsonResponse({
                'status': '400',
                'message': '送货人地址不存在',
            }, status=200)
        if current_mer.status != 1:
            return JsonResponse({
                'status': '400',
                'message': '商品已经售出',
            }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '传入的id有误',
        }, status=200)

    sid = transaction.savepoint()
    try:
        new_transaction = Transaction.objects.create(
            transaction_sender=current_sender,
            transaction_receiver=current_user,
            transaction_merchandise=current_mer,
            total_price=current_mer.price + current_mer.deliver_price,
            sender_location=send_addr,
            receiver_location=rec_addr
        )
        new_transaction.save()
        current_mer.status = 5
        current_mer.save()
        if identify_code:
            conn = get_redis_connection('default')
            key = 'identify_code_{}'.format(identify_code)
            tra_list = conn.get(key)
            if not tra_list:
                tra_list = []
            else:
                tra_list = literal_eval(tra_list)
            tra_list.append(new_transaction.id)
            conn.set(key, str(tra_list))
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '创建订单失败',
        }, status=200)
    transaction.savepoint_commit(sid)
    if current_sender.credit_points < 6:
        send_notice(current_user.id, '商家信誉不足，推荐使用虚拟货币进行支付', current_user=current_user, rela_mer=current_mer)
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'transaction_id': signer.sign_object(new_transaction.id)
    }, status=200)


@transaction.atomic
@login_required()
def cancel_transaction(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('tra_id', None)
    cancel_reason = request.POST.get('cancel_reason', None)
    if not current_tra_id:
        return JsonResponse({
            'status': '400',
            'message': '传入的post字段不全',
        }, status=200)
    if not check_args_valid([current_tra_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    if not cancel_reason:
        cancel_reason = '用户未说明原因'
    try:
        signer = TimestampSigner()
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
        if current_tra.status > 1:
            return JsonResponse({
                'status': '400',
                'message': '订单已经被付款，请申请退款',
            }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '传入的id有误',
        }, status=200)
    if current_tra.transaction_receiver != current_user:
        return JsonResponse({
            'status': '400',
            'message': '不是你的订单',
        }, status=200)
    sid = transaction.savepoint()
    sender_id = current_tra.transaction_sender.id
    mer_name = current_tra.transaction_merchandise.name
    try:
        current_mer = current_tra.transaction_merchandise
        current_mer.status = 1
        current_mer.save()
        current_tra.delete()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(sender_id, '商品{}的订单被取消，取消原因为:{}'.format(mer_name, cancel_reason), current_user=current_user, rela_mer=current_mer)
    send_notice(current_user.id, '商品{}的订单取消成功'.format(mer_name), current_user=current_user, rela_mer=current_mer)
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)


@transaction.atomic
@login_required()
def commit_transaction_total(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    if current_user.credit_points < 0:
        return JsonResponse({
            'status': '400',
            'message': '信誉分不足，支付被禁止',
        }, status=200)
    current_identify_code = request.POST.get('current_identify_code', None)
    pay_password = request.POST.get('pay_password', None)
    if not all((current_identify_code, pay_password)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_identify_code, pay_password]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    pay_password = hash_code(pay_password)
    if current_user.pay_password != pay_password:
        return JsonResponse({
            'status': '400',
            'message': '密码错误',
        }, status=200)
    rec_address_id = request.POST.get('rec_address_id', None)
    conn = get_redis_connection('default')
    key = 'identify_code_{}'.format(current_identify_code)
    tra_list = conn.get(key)
    if not tra_list:
        tra_list = []
    else:
        tra_list = literal_eval(tra_list)
    signer = TimestampSigner()
    cur_tra_list = []
    for i in tra_list:
        this_tra = Transaction.objects.get(id=i)
        if this_tra.transaction_merchandise.upload_user == current_user:
            return JsonResponse({
            'status': '400',
            'message': '不能买自己的商品',
        }, status=200)
        cur_tra_list.append(Transaction.objects.get(id=i))
    sum_price = 0
    for current_tra in cur_tra_list:
        sum_price += current_tra.total_price
    if current_user.money < sum_price:
        return JsonResponse({
            'status': '400',
            'message': '余额不足，请充值',
        }, status=200)
    sid = transaction.savepoint()
    if rec_address_id:
        rec_address_id = signer.unsign_object(rec_address_id)
        try:
            change_location = user.models.Address.objects.get(id=rec_address_id)
        except:
            return JsonResponse({
                'status': '400',
                'message': '地址id错误',
            }, status=200)
    for current_tra in cur_tra_list:
        if current_tra.status != 1:
            return JsonResponse({
                'status': '400',
                'message': '订单异常',
            }, status=200)
        try:
            current_tra.receiver_location = change_location
            if current_tra.transaction_merchandise.status != 5:
                raise Exception
            current_user.money -= current_tra.total_price
            current_tra.pay_time = django.utils.timezone.now()
            current_tra.transaction_merchandise.status = 2
            current_tra.status = 2
            current_tra.pay_method = 3
            current_tra.save()
            current_user.save()
            current_tra.transaction_merchandise.save()
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return JsonResponse({
                'status': '400',
                'message': '服务器错误',
            }, status=200)
    transaction.savepoint_commit(sid)
    for mer_id in tra_list:
        server_cart_del(mer_id, current_user.id)
    for current_tra in cur_tra_list:
        send_notice(current_tra.transaction_sender.id, '商品{}被支付，请尽快发货'.format(current_tra.transaction_merchandise.name),
                    current_user=current_user, rela_mer=current_tra.transaction_merchandise)
        send_notice(current_user.id, '感谢您在本平台购买商品{},将提醒卖家尽快发货'.format(current_tra.transaction_merchandise.name),
                    current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    conn.delete(key)
    return JsonResponse({
            'status': '200',
            'message': '成功',
        }, status=200)


@transaction.atomic
@login_required()
def commit_transaction_virtual(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    if current_user.credit_points < 0:
        return JsonResponse({
            'status': '400',
            'message': '信誉分不足，支付被禁止',
        }, status=200)
    current_tra_id = request.POST.get('tra_id', None)
    pay_password = request.POST.get('pay_password', None)
    if not all((current_tra_id, pay_password)):
        return JsonResponse({
            'status': '200',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_tra_id, pay_password]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    rec_address_id = request.POST.get('rec_address_id', None)
    signer = TimestampSigner()

    try:
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    pay_password = hash_code(pay_password)
    if current_user.pay_password != pay_password:
        return JsonResponse({
            'status': '400',
            'message': '密码错误',
        }, status=200)

    if rec_address_id:
        rec_address_id = signer.unsign_object(rec_address_id)
        try:
            current_tra.receiver_location = user.models.Address.objects.get(id=rec_address_id)
        except:
            return JsonResponse({
                'status': '400',
                'message': '地址id错误',
            }, status=200)

    if current_tra.status != 1:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_user.money < current_tra.total_price:
        return JsonResponse({
            'status': '400',
            'message': '余额不足，请充值',
        }, status=200)
    sid = transaction.savepoint()
    try:
        if current_tra.transaction_merchandise.status != 5:
            raise Exception
        current_user.money -= current_tra.total_price
        current_tra.pay_time = django.utils.timezone.now()
        current_tra.transaction_merchandise.status = 2
        current_tra.status = 2
        current_tra.pay_method = 3
        current_tra.save()
        current_user.save()
        current_tra.transaction_merchandise.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    server_cart_del(current_tra.transaction_merchandise.id, current_user.id)
    send_notice(current_tra.transaction_sender.id, '商品{}被支付，请尽快发货'.format(current_tra.transaction_merchandise.name),
                current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_user.id, '感谢您在本平台购买商品{},将提醒卖家尽快发货'.format(current_tra.transaction_merchandise.name),
                current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
            'status': '200',
            'message': '成功',
        }, status=200)


@transaction.atomic
@login_required()
def commit_transaction_face(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('tra_id', None)
    if current_user.credit_points < 0:
        return JsonResponse({
            'status': '400',
            'message': '信誉分不足，支付被禁止',
        }, status=200)
    if current_user.credit_points < 6:
        return JsonResponse({
            'status': '400',
            'message': '信誉分不足，只支持虚拟货币',
        }, status=200)
    if not current_tra_id:
        return JsonResponse({
            'status': '200',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_tra_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    rec_address_id = request.POST.get('rec_address_id', None)
    signer = TimestampSigner()
    try:
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if not current_tra.transaction_merchandise.allow_face_trade:
        return JsonResponse({
            'status': '400',
            'message': '商品不允许面对面交易',
        }, status=200)
    if rec_address_id:
        rec_address_id = signer.unsign_object(rec_address_id)
        try:
            current_tra.receiver_location = user.models.Address.objects.get(id=rec_address_id)
        except:
            return JsonResponse({
                'status': '400',
                'message': '地址id错误',
            }, status=200)

    if current_tra.status != 1:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    sid = transaction.savepoint()
    try:
        if current_tra.transaction_merchandise.status != 5:
            raise Exception
        current_tra.pay_time = django.utils.timezone.now()
        current_tra.transaction_merchandise.status = 2
        current_tra.status = 2
        current_tra.pay_method = 1
        current_tra.save()
        current_user.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    server_cart_del(current_tra.transaction_merchandise.id, current_user.id)
    send_notice(current_tra.transaction_sender.id, '商品{}被{}下单，支付方式为面对面支付，请尽快发货'.format(current_tra.transaction_merchandise.name, current_user.name),
                current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_user.id, '感谢您在本平台购买商品{},将提醒卖家尽快发货'.format(current_tra.transaction_merchandise.name),
                current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
            'status': '200',
            'message': '成功',
        }, status=200)


# @login_required()
# def commit_transaction_QR_code_start(request:HttpRequest):
#     current_user = user.models.User.objects.get(id=request.session.get('user_id'))
#     current_tra_id = request.POST.get('tra_id', None)
#     if not current_tra_id:
#         return JsonResponse({
#             'status': '200',
#             'message': 'POST字段不全',
#         }, status=200)
#     rec_address_id = request.POST.get('rec_address_id', None)
#     signer = TimestampSigner()
#     try:
#         current_tra_id = signer.unsign_object(current_tra_id)
#         current_tra = Transaction.objects.get(id=current_tra_id)
#     except:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     if rec_address_id:
#         rec_address_id = signer.unsign_object(rec_address_id)
#         try:
#             current_tra.receiver_location = user.models.Address.objects.get(id=rec_address_id)
#         except:
#             return JsonResponse({
#                 'status': '400',
#                 'message': '地址id错误',
#             }, status=200)
#     if current_tra.status != 1:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     if current_tra.QRPayStatus != 1:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     if not is_user_online(current_tra.transaction_merchandise.upload_user.id):
#         return JsonResponse({
#             'status': '400',
#             'message': '用户不在线',
#         }, status=200)
#     send_notice(current_tra.transaction_merchandise.upload_user.id,
#                 '商品{}想要被{}通过二维码方式付款，请确认自己可以处理,剩余时间为{}s'.format(
#                     current_tra.transaction_merchandise.name, current_user.name,
#                     3600 - (django.utils.timezone.now() - current_tra.create_time).seconds))
#     current_tra.QRPayStatus = 2
#     current_tra.save()
#     return JsonResponse({
#             'status': '200',
#             'message': '成功',
#         }, status=200)
#
#
# @login_required()
# def commit_transaction_QR_code_ready(request:HttpRequest):
#     current_user = user.models.User.objects.get(id=request.session.get('user_id'))
#     current_tra_id = request.POST.get('tra_id', None)
#     if not current_tra_id:
#         return JsonResponse({
#             'status': '200',
#             'message': 'POST字段不全',
#         }, status=200)
#     signer = TimestampSigner()
#     try:
#         current_tra_id = signer.unsign_object(current_tra_id)
#         current_tra = Transaction.objects.get(id=current_tra_id)
#     except:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     if current_tra.status != 1:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     if current_tra.QRPayStatus != 2:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     send_notice(current_tra.transaction_receiver.id,
#                 '商品{}现在可以通过二维码方式付款了'.format(current_tra.transaction_merchandise.name))
#     current_tra.QRPayStatus = 3
#     current_tra.save()
#     return JsonResponse({
#             'status': '200',
#             'message': '成功',
#         }, status=200)


@transaction.atomic
@login_required()
def commit_transaction_QR_code_commit(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('tra_id', None)
    current_pay_prove = request.FILES.get('current_pay_prove', None)
    if current_user.credit_points < 0:
        return JsonResponse({
            'status': '400',
            'message': '信誉分不足，支付被禁止',
        }, status=200)
    if current_user.credit_points < 6:
        return JsonResponse({
            'status': '400',
            'message': '信誉分不足，只支持虚拟货币',
        }, status=200)
    if not all((current_tra_id, current_pay_prove)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_tra_id, current_pay_prove]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    rec_address_id = request.POST.get('rec_address_id', None)
    try:
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if rec_address_id:
        rec_address_id = signer.unsign_object(rec_address_id)
        try:
            current_tra.receiver_location = user.models.Address.objects.get(id=rec_address_id)
        except:
            return JsonResponse({
                'status': '400',
                'message': '地址id错误',
            }, status=200)
    if current_tra.status != 1:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    # if current_tra.QRPayStatus != 3:
    #     return JsonResponse({
    #         'status': '400',
    #         'message': '订单异常',
    #     }, status=200)
    sid = transaction.savepoint()
    try:
        if current_tra.transaction_merchandise.status != 5:
            raise Exception
        current_tra.pay_time = django.utils.timezone.now()
        current_tra.transaction_merchandise.status = 2
        current_tra.transaction_merchandise.save()
        current_tra.status = 2
        current_tra.pay_method = 2
        current_tra.pay_prove =current_pay_prove
        current_tra.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    server_cart_del(current_tra.transaction_merchandise.id, current_user.id)
    send_notice(current_tra.transaction_sender.id,
                '商品{}被通过二维码下单，请在10Min内确认'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_user.id, '感谢您在本平台购买商品{},将提醒卖家尽快发货'.format(current_tra.transaction_merchandise.name),
                current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)



# @transaction.atomic
# @login_required()
# def commit_transaction_QR_code_commit_receive(request:HttpRequest):
#     current_user = user.models.User.objects.get(id=request.session.get('user_id'))
#     current_tra_id = request.POST.get('tra_id', None)
#     if not current_tra_id:
#         return JsonResponse({
#             'status': '200',
#             'message': 'POST字段不全',
#         }, status=200)
#     signer = TimestampSigner()
#     try:
#         current_tra_id = signer.unsign_object(current_tra_id)
#         current_tra = Transaction.objects.get(id=current_tra_id)
#     except:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     if current_tra.status != 7:
#         return JsonResponse({
#             'status': '400',
#             'message': '订单异常',
#         }, status=200)
#     sid = transaction.savepoint()
#     try:
#         current_tra.transaction_merchandise.status = 2
#         current_tra.status = 2
#         current_tra.comfirm_time = django.utils.timezone.now()
#         current_tra.save()
#     except Exception as e:
#         transaction.savepoint_rollback(sid)
#         return JsonResponse({
#             'status': '400',
#             'message': '服务器错误',
#         }, status=200)
#     transaction.savepoint_commit(sid)
#     send_notice(current_tra.transaction_receiver.id,
#                 '商品{}被卖家确认，即将发货'.format(current_tra.transaction_merchandise.name))
#     return JsonResponse({
#         'status': '200',
#         'message': '成功',
#     }, status=200)


@transaction.atomic
@login_required()
def already_send_transaction(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('current_tra_id', None)
    if not current_tra_id:
        return JsonResponse({
            'status': '400',
            'message': '订单不存在',
        }, status=200)
    if not check_args_valid([current_tra_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    try:
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_tra.status != 2:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_tra.transaction_sender.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的订单',
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_tra.status = 3
        current_tra.send_time = django.utils.timezone.now()
        if current_tra.pay_method == 2:
            current_tra.comfirm_time = django.utils.timezone.now()
        current_tra.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_tra.transaction_receiver.id,
                '商品{}被已被送达，请尽快确认查收'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_tra.transaction_sender.id,
                '商品{}被状态以改为送达,将等待买家确认'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)


@transaction.atomic
@login_required()
def already_receive_transaction(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('current_tra_id', None)
    if not current_tra_id:
        return JsonResponse({
            'status': '400',
            'message': '订单不存在',
        }, status=200)
    signer = TimestampSigner()
    try:
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_tra.status != 3:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_tra.transaction_receiver.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的订单',
        }, status=200)
    sid = transaction.savepoint()
    try:
        # current_tra.pay_time = django.utils.timezone.now()
        # current_tra.transaction_merchandise.status = 2
        current_tra.status = 4
        # current_tra.pay_method = 1
        current_tra.save()
        # current_user.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_tra.transaction_receiver.id,
                '商品{}确认收货成功'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_tra.transaction_sender.id,
                '商品{}已被买家确认收货，将等待买家评价'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)


#默认好评前端生成
@transaction.atomic
@login_required()
def comment_transaction(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('current_tra_id', None)
    comment_content = request.POST.get('comment_content', None)
    comment_level_mer = request.POST.get('comment_level_mer', None)
    comment_level_attitude = request.POST.get('comment_level_attitude', None)
    comment_level_tra = request.POST.get('comment_level_tra', None)
    if not all((current_tra_id, comment_content, comment_level_mer, comment_level_attitude, comment_level_tra)):
        return JsonResponse({
            'status': '400',
                'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_tra_id, comment_content, comment_level_mer, comment_level_attitude, comment_level_tra]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    try:
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
        comment_level_tra = int(float(comment_level_tra))
        comment_level_mer = int(float(comment_level_mer))
        comment_level_attitude = int(float(comment_level_attitude))
    except:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_tra.status != 4:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_tra.transaction_receiver.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的订单',
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_tra.status = 5
        current_mer = current_tra.transaction_merchandise
        current_mer.status = 4
        current_mer.save()
        current_tra.save()
        new_comment = user.models.Comment.objects.create(
            comment_content=comment_content,
            comment_user=current_user,
            comment_target=current_tra.transaction_merchandise.upload_user,
            comment_transaction=current_tra,
            comment_level_tra=comment_level_tra,
            comment_level_mer=comment_level_mer,
            comment_level_attitude=comment_level_attitude
        )
        new_comment.save()
        cur_tra_uploader = current_tra.transaction_merchandise.upload_user
        comment_number = cur_tra_uploader.comment_number
        cur_tra_uploader.stars_for_attitude = (cur_tra_uploader.stars_for_attitude
                                               * (comment_number+10) + comment_level_attitude) / (comment_number+11)
        cur_tra_uploader.stars_for_deliver = (cur_tra_uploader.stars_for_deliver
                                               * (comment_number + 10) + comment_level_tra) / (comment_number + 11)
        cur_tra_uploader.stars_for_good = (cur_tra_uploader.stars_for_good
                                               * (comment_number + 10) + comment_level_mer) / (comment_number + 11)
        if current_tra.pay_method == 3:
            cur_tra_uploader.money += current_tra.total_price
        cur_tra_uploader.comment_number += 1
        cur_tra_uploader.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    conn = get_redis_connection('default')
    key = 'today_finish_order_num_{}'.format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    key2 = 'today_finish_order_list{}'.format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    today_order_num = conn.get(key)
    if today_order_num:
        today_order_num = int(today_order_num)
        today_order_num += 1
    else:
        today_order_num = 1
    conn.set(key, today_order_num)
    today_order_list = conn.get(key2)
    if today_order_list:
        today_order_list = literal_eval(today_order_list)
        today_order_list.append(django.utils.timezone.now().strftime('%Y-%m-%d %X'))
    else:
        today_order_list = []
        today_order_list.append(django.utils.timezone.now().strftime('%Y-%m-%d %X'))
    conn.set(key2, str(today_order_list))
    transaction.savepoint_commit(sid)
    send_notice(current_tra.transaction_receiver.id,
                '商品{}评价成功'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_tra.transaction_sender.id,
                '商品{}已被买家评价'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)


@transaction.atomic
@login_required()
def transaction_has_problem(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_tra_id = request.POST.get('current_tra_id', None)
    problem_description = request.POST.get('problem_description', None)
    problem_type = request.POST.get('problem_type', None)
    if not all((current_tra_id, problem_type, problem_description)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_tra_id, problem_type, problem_description]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        signer = TimestampSigner()
        current_tra_id = signer.unsign_object(current_tra_id)
        current_tra = Transaction.objects.get(id=current_tra_id)
        problem_type = int(problem_type)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id解码错误',
        }, status=200)
    if current_tra.status > 4 or current_tra.has_problem:
        return JsonResponse({
            'status': '400',
            'message': '订单状态错误',
        }, status=200)
    if current_user.id != current_tra.transaction_sender.id and current_user.id != current_tra.transaction_receiver.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的transaction',
        }, status=200)
    if problem_type == 1:
        if current_tra.status < 2 or current_tra.pay_method != 3:
            return JsonResponse({
                'status': '400',
                'message': '订单状态异常',
            }, status=200)
    elif problem_type == 2:
        if current_tra.status < 2 or current_tra.pay_method != 1:
            return JsonResponse({
                'status': '400',
                'message': '订单状态异常',
            }, status=200)
    elif problem_type == 3:
        if current_tra.pay_method != 2 or current_tra.status != 2:
            return JsonResponse({
                'status': '400',
                'message': '订单状态异常',
            }, status=200)
    elif problem_type == 4:
        if current_tra.status < 2:
            return JsonResponse({
                'status': '400',
                'message': '订单状态异常',
            }, status=200)
    elif problem_type == 5:
        if current_tra.status != 5:
            return JsonResponse({
                'status': '400',
                'message': '订单状态异常',
            }, status=200)
    else:
        if current_tra.status == 6:
            return JsonResponse({
                'status': '400',
                'message': '订单状态异常',
            }, status=200)
        if problem_type != 6:
            return JsonResponse({
                'status': '400',
                'message': '问题类型异常',
            }, status=200)
    sid = transaction.savepoint()
    try:
        new_problem = TransactionProblem.objects.create(
            problem_description=problem_description,
            problem_transaction=current_tra,
            problem_uploader=current_user,
            problem_type=problem_type,
            transaction_last_status=current_tra.status
        )
        # current_tra.status = 6
        current_tra.has_problem = True
        current_tra.rela_problem_id = new_problem.id
        current_tra.rela_problem_description = new_problem.problem_description
        current_tra.rela_problem_type = new_problem.problem_type
        current_tra.has_problem_before = True
        current_tra.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_tra.transaction_receiver.id,
                '商品{}所涉及的交易进入问题处理阶段'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    send_notice(current_tra.transaction_sender.id,
                '商品{}所涉及的交易进入问题处理阶段'.format(current_tra.transaction_merchandise.name), current_user=current_user, rela_mer=current_tra.transaction_merchandise)
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)