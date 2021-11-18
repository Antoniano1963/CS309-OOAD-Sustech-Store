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
from django.db.models import Q
from order.models import Transaction, TransactionProblem
# Create your views here.


@login_required(status=3)
def problems_list(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    # if current_user.user_identify != 0:
    #     return JsonResponse({
    #         'status': '500',
    #         'message': '不是管理员',
    #     }, status=500)
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
    problems_lists = TransactionProblem.objects.filter(problem_status=1)
    return_list = []
    for pro in problems_lists.all():
        return_list.append(pro.get_detail_info())
    has_next = False
    if end_position < len(return_list):
        has_next = True
    return JsonResponse({
            'status': '200',
            'message': '查询成功',
            'return_list': return_list[start_position:end_position],
            'has_next': has_next,
        }, status=200)


@transaction.atomic
@login_required(status=3)
def handle_problem(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    # if current_user.user_identify != 0:
    #     return JsonResponse({
    #         'status': '500',
    #         'message': '不是管理员',
    #     }, status=500)
    superuser_log = request.POST.get('superuser_log', None)
    problem_id = request.POST.get('problem_id', None)
    problem_role = request.POST.get('problem_role', None)
    if not all((superuser_log, problem_role, problem_id)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    try:
        problem_role = int(problem_role)
        signer = TimestampSigner()
        problem_id = signer.unsign_object(problem_id)
        current_problem = TransactionProblem.objects.get(id=problem_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id错误',
        }, status=200)
    if current_problem.problem_type == 1:
        if problem_role == 2:
            sid = transaction.savepoint()
            try:
                payer = current_problem.problem_transaction.transaction_receiver
                payer.money += current_problem.problem_transaction.total_price
                payer.save()
                current_problem.problem_role = problem_role
                current_problem.superuser_log = superuser_log
                current_problem.handle_superuser = current_user
                current_problem.problem_user = current_problem.problem_transaction.transaction_sender
                current_problem.problem_transaction.transaction_sender.problem_number += 1
                current_problem.problem_transaction.transaction_sender.save()
                current_problem.problem_status = 2
                current_problem.save()
                current_problem.problem_transaction.has_problem = False
                current_problem.problem_transaction.save()
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse({
                    'status': '400',
                    'message': '服务器错误',
                }, status=200)
            transaction.savepoint_commit(sid)
            send_notice(payer.id,
                        '商品{}已经退款处理'.format(current_problem.problem_transaction.transaction_merchandise.name))
            send_notice(current_problem.problem_transaction.transaction_sender.id,
                        '商品{}已经退款处理'.format(current_problem.problem_transaction.transaction_merchandise.name))
        else:
            payer = current_problem.problem_transaction.transaction_receiver
            send_notice(payer.id,
                        '商品{}退款被拒绝'.format(current_problem.problem_transaction.transaction_merchandise.name))
            send_notice(current_problem.problem_transaction.transaction_sender.id,
                        '商品{}退款被拒绝'.format(current_problem.problem_transaction.transaction_merchandise.name))

            sid = transaction.savepoint()
            try:
                current_problem.problem_transaction.has_problem = False
                current_problem.problem_transaction.save()
                current_problem.problem_role = problem_role
                current_problem.superuser_log = superuser_log
                current_problem.handle_superuser = current_user
                current_problem.problem_user = payer
                current_problem.problem_status = 2
                current_problem.save()
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse({
                    'status': '400',
                    'message': '服务器错误',
                }, status=200)
            transaction.savepoint_commit(sid)
    else:
        if problem_role == 1:
            sid = transaction.savepoint()
            try:
                receiver = current_problem.problem_transaction.transaction_receiver
                receiver.problem_number += 1
                receiver.save()
                current_problem.problem_role = problem_role
                current_problem.superuser_log = superuser_log
                current_problem.handle_superuser = current_user
                current_problem.save()
                current_problem.problem_transaction.has_problem = False
                current_problem.problem_transaction.save()
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse({
                    'status': '400',
                    'message': '服务器错误',
                }, status=200)
            transaction.savepoint_commit(sid)
            send_notice(current_problem.problem_transaction.transaction_receiver.id,
                        '商品{}问题处理结果发布'.format(current_problem.problem_transaction.transaction_merchandise.name))
            send_notice(current_problem.problem_transaction.transaction_sender.id,
                        '商品{}问题处理结果发布'.format(current_problem.problem_transaction.transaction_merchandise.name))
        else:
            sid = transaction.savepoint()
            try:
                sender = current_problem.problem_transaction.transaction_sender
                sender.problem_number += 1
                sender.save()
                current_problem.problem_role = problem_role
                current_problem.superuser_log = superuser_log
                current_problem.handle_superuser = current_user
                current_problem.save()
                current_problem.problem_transaction.has_problem = False
                current_problem.problem_transaction.save()
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse({
                    'status': '400',
                    'message': '服务器错误',
                }, status=200)
            transaction.savepoint_commit(sid)
            send_notice(current_problem.problem_transaction.transaction_receiver.id,
                        '商品{}问题处理结果发布'.format(current_problem.problem_transaction.transaction_merchandise.name))
            send_notice(current_problem.problem_transaction.transaction_sender.id,
                        '商品{}问题处理结果发布'.format(current_problem.problem_transaction.transaction_merchandise.name))
    return JsonResponse({
                'status': '200',
                'message': '成功',
            }, status=200)


@login_required(status=3)
def website_info(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    # if current_user.user_identify != 0:
    #     return JsonResponse({
    #         'status': '500',
    #         'message': '不是管理员',
    #     }, status=500)
    key1 = 'today_finish_order_num_{}'.format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    key2 = "today_view_num_{}".format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    key3 = 'online_num_{}'.format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    conn = get_redis_connection("default")
    finish_order_num = conn.get(key1)
    view_num = conn.get(key2)
    online_num = conn.get(key3)
    return JsonResponse({
            'status': '200',
            'message': '成功',
            'finish_order_num': finish_order_num,
            'view_num': view_num,
            'online_num': online_num
        }, status=200)