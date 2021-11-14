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

@transaction.atomic
@login_required()
def handle_problem(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    if current_user.user_identify != 0:
        return JsonResponse({
            'status': '500',
            'message': '不是管理员',
        }, status=500)
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
            current_problem.problem_role = problem_role
            current_problem.superuser_log = superuser_log
            current_problem.handle_superuser = current_user
            current_problem.problem_user = current_problem.problem_transaction.transaction_sender
            current_problem.problem_transaction.transaction_sender.problem_number += 1
            current_problem.problem_transaction.transaction_sender.save()
            current_problem.save()
            return JsonResponse({
                'status': '200',
                'message': '成功',
            }, status=200)
        else:
            payer = current_problem.problem_transaction.transaction_receiver
            send_notice(payer.id,
                        '商品{}退款被拒绝'.format(current_problem.problem_transaction.transaction_merchandise.name))
            send_notice(current_problem.problem_transaction.transaction_sender.id,
                        '商品{}退款被拒绝'.format(current_problem.problem_transaction.transaction_merchandise.name))
            current_problem.problem_role = problem_role
            current_problem.superuser_log = superuser_log
            current_problem.handle_superuser = current_user
            current_problem.problem_user = payer
            current_problem.save()
            sid = transaction.savepoint()
            try:
                current_problem.problem_transaction.status = 7
                current_problem.problem_transaction.save()
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse({
                    'status': '400',
                    'message': '服务器错误',
                }, status=200)
            transaction.savepoint_commit(sid)
            return JsonResponse({
                'status': '200',
                'message': '成功',
            }, status=200)
    else:
        if problem_role == 1:
            receiver = current_problem.problem_transaction.transaction_receiver
            receiver.problem_number += 1
            receiver.save()
            current_problem.problem_role = problem_role
            current_problem.superuser_log = superuser_log
            current_problem.handle_superuser = current_user
            current_problem.save()
        else:
            sender = current_problem.problem_transaction.transaction_sender
            sender.problem_number += 1
            sender.save()
            current_problem.problem_role = problem_role
            current_problem.superuser_log = superuser_log
            current_problem.handle_superuser = current_user
            current_problem.save()
    return JsonResponse({
                'status': '200',
                'message': '成功',
            }, status=200)