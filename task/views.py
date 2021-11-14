from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from Final_Project1.decotators.login_required import login_required
import user.models
import order.models
import task.models
from django.db import transaction
from django.core.signing import TimestampSigner
from task.utils import start_task_dialogue
from chat.utils import *
# Create your views here.


@transaction.atomic
@login_required(status=1)
def release_task_transaction(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    tra_id = request.POST.get('tra_id', None)
    ddl_time = request.POST.get('ddl_time', None)
    price = request.POST.get('price', None)
    description = request.POST.get('description', None)
    name = request.POST.get('name', None)
    if not all((tra_id, ddl_time, price, description, name)):
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    if current_user.money < price:
        return JsonResponse({
            'status': '400',
            'message': '余额不足'
        }, status=200)
    try:
        tra_id = signer.unsign_object(tra_id)
        cur_transaction = order.models.Transaction.objects.get(id=tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'transaction不存在'
        }, status=200)
    has_task = task.models.Task.objects.filter(task_status__exact=1).filter(relation_transaction=cur_transaction)
    if has_task:
        return JsonResponse({
            'status': '400',
            'message': 'transaction已经发布过task'
        }, status=200)
    sid = transaction.savepoint()
    try:
        new_task = task.models.Task.objects.create(
            name=name,
            task_type=1,
            relation_transaction=cur_transaction,
            description=description,
            upload_user=current_user,
            ddl_time=ddl_time,
            receive_user=cur_transaction.transaction_receiver,
            receive_addr=cur_transaction.receiver_location,
            sender_addr=cur_transaction.sender_location,
            price=price,
        )
        new_task.save()
        current_user.money -= price
        current_user.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '非法字段'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}发布成功，请尽快发货'.format(name))
    return JsonResponse({
        'status': '200',
        'message': '创建成功',
        'task_id': signer.sign_object(new_task.id)
    }, status=200)


@transaction.atomic
@login_required(status=1)
def release_task_others(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    ddl_time = request.POST.get('ddl_time', None)
    price = request.POST.get('price', None)
    description = request.POST.get('description', None)
    name = request.POST.get('name', None)
    sender_addr_id = request.POST.get("sender_addr_id", None)
    receive_addr_id = request.POST.get("receive_addr_id", None)
    receive_time = request.POST.get("receive_time", None)
    if not all((sender_addr_id, ddl_time, price, description, name, receive_addr_id)):
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    if current_user.money < price:
        return JsonResponse({
            'status': '400',
            'message': '余额不足'
        }, status=200)
    try:
        sender_addr_id = signer.unsign_object(sender_addr_id)
        receive_addr_id = signer.unsign_object(receive_addr_id)
        sender_addr = user.models.Address.objects.get(id=sender_addr_id)
        receive_addr = user.models.Address.objects.get(id=receive_addr_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'transaction不存在'
        }, status=200)
    sid = transaction.savepoint()
    try:
        new_task = task.models.Task.objects.create(
            name=name,
            task_type=2,
            description=description,
            ddl_time=ddl_time,
            receive_user=current_user,
            receive_addr=receive_addr,
            sender_addr=sender_addr,
            receive_time=receive_time,
            upload_user=current_user,
            price=price
        )
        new_task.save()
        current_user.money -= price
        current_user.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '非法字段'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}发布成功，请尽快发货'.format(name))
    return JsonResponse({
        'status': '200',
        'message': '创建成功',
        'task_id': signer.sign_object(new_task.id)
    }, status=200)



@transaction.atomic
@login_required(status=1)
def cancel_task(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    task_id = request.POST.get('task_id', None)
    if not task_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    task_name = current_task.name
    sid = transaction.savepoint()
    try:
        current_user.money += current_task.price
        current_user.save()
        current_task.delete()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}取消成功'.format(task_name))
    return JsonResponse({
        'status': '200',
        'message': '取消成功',
    }, status=200)


@transaction.atomic
@login_required(status=1)
def get_task(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    task_id = request.POST.get('task_id', None)
    if not task_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    sid = transaction.savepoint()
    try:
        if current_task.task_status != 7:
            raise Exception
        current_task.sender_user = current_user
        cur_dialogue = start_task_dialogue(current_user, current_task.upload_user, task)
        current_task.dialogue_between_up_sender = cur_dialogue
        current_task.task_status = 1
        current_task.save()
    except:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '非法字段'
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}领取成功，请尽快处理'.format(current_task.name))
    send_notice(current_task.upload_user.id, '任务{}被用户{}接受，请尽快处理'.format(current_task.name, current_user.name))
    return JsonResponse({
        'status': '200',
        'message': '领取成功',
    }, status=200)


@transaction.atomic
@login_required(status=1)
def task_get_object(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    task_id = request.POST.get('task_id', None)
    if not task_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    if current_task.sender_user.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的task'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_task.task_status = 2
        current_task.save()
    except:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}交予成功'.format(current_task.name))
    send_notice(current_task.upload_user.id,
                '您发布的任务{}物品被人领取，请确认'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '创建成功',
    }, status=200)


@transaction.atomic
@login_required(status=1)
def task_send_object(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    task_id = request.POST.get('task_id', None)
    if not task_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    if current_task.sender_user.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的task'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_task.task_status = 3
        current_task.save()
    except:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}交予成功'.format(current_task.name))
    send_notice(current_task.upload_user.id,
                '您发布的任务{}物品被人送达，请确认'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '创建成功',
    }, status=200)


@transaction.atomic
@login_required(status=1)
def task_send_object(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    task_id = request.POST.get('task_id', None)
    if not task_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    if current_task.upload_user.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的task'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_task.task_status = 4
        current_task.save()
        current_task.sender_user.money += current_task.price
        current_task.sender_user.save()
    except:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
    send_notice(current_task.sender_user.id, '任务{}已经被确认收货'.format(current_task.name))
    send_notice(current_user.id,
                '您发布的任务{}以确认确认'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '创建成功',
    }, status=200)


@transaction.atomic
@login_required()
def task_comment(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_task_id = request.POST.get('task_id', None)
    comment_content = request.POST.get('comment_content', None)
    comment_level = request.POST.get('comment_level', None)
    if not all((current_task_id, comment_content, comment_level)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    signer = TimestampSigner()
    try:
        current_task_id = signer.unsign_object(current_task_id)
        current_task = task.models.Task.objects.get(id=current_task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '任务异常',
        }, status=200)
    if current_task.status != 4:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_task.upload_user.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的订单',
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_task.status = 5
        current_task.save()
        new_comment = user.models.CommentTask.objects.create(
            comment_content=comment_content,
            comment_user=current_user,
            comment_target=current_task.sender_user,
            comment_level=comment_level
        )
        new_comment.save()
        task_uploader = current_task.sender_user
        comment_number = task_uploader.comment_number_for_task
        task_uploader.stars_for_task = (task_uploader.stars_for_task * comment_number +
                                        comment_level) / (comment_number+1)
        task_uploader.comment_number_for_task += 1
        task_uploader.save()

    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({
            'status': '400',
            'message': '服务器错误',
        }, status=200)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id,
                '任务{}评价成功'.format(current_task.name))
    send_notice(current_task.sender_user.id,
                '任务{}已被评价'.format(current_task.name.name))
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)
