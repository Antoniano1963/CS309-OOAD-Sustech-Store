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
from django.db.models import Q
import datetime
import django.utils.timezone
from utils.check_args_valid import *
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
    if not check_args_valid([tra_id, ddl_time, price, description, name]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    try:
        price = float(price)
    except:
        JsonResponse({
            'status': '400',
            'message': '字段异常',
        }, status=200)
    if current_user.money < price:
        return JsonResponse({
            'status': '400',
            'message': '余额不足'
        }, status=200)
    try:
        ddl_time = datetime.datetime.strptime(ddl_time, '%Y-%m-%d %X')
        tra_id = signer.unsign_object(tra_id)
        cur_transaction = order.models.Transaction.objects.get(id=tra_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'transaction不存在'
        }, status=200)
    if current_user != cur_transaction.transaction_sender:
        return JsonResponse({
            'status': '400',
            'message': '不是你发布的task'
        }, status=200)
    has_task = task.models.Task.objects.filter(relation_transaction=cur_transaction)
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
        cur_transaction.has_task = True
        cur_transaction.save()
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
    if not check_args_valid([sender_addr_id, ddl_time, price, description, name, receive_addr_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    price = float(price)
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
    if not check_args_valid([task_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
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



@login_required(status=1)
def get_task_list(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    method_list = ["new", "price", 'default']
    task_type_list = [1, 2]
    task_type = request.POST.get('task_type', None)
    sort_method = request.POST.get('sort_method', 'default')
    search_str = request.POST.get('search_str', None)
    if sort_method not in method_list:
        return JsonResponse({
            'status': '400',
            'message': '字段值错误'
        }, status=200)
    if task_type:
        task_type = int(task_type)
        if task_type not in task_type_list:
            return JsonResponse({
                'status': '400',
                'message': '字段值错误'
            }, status=200)
    # try:
    if task_type:
        mer_list = task.models.Task.objects.get_tasks_by_class(
            task_type=task_type, sort=sort_method
        )
    else:
        mer_list = task.models.Task.objects.get_tasks_by_class(
            sort=sort_method
        )
    if search_str:
        mer_list_new = mer_list.filter(Q(name__contains=search_str) |Q(description__contains=search_str))
    else:
        mer_list_new = mer_list
    return_list = []
    if mer_list_new:
        for i in mer_list_new.all():
            return_list.append(i.get_simple_info())
    start_position = int(request.POST.get('start_position', 0))
    end_position = int(request.POST.get('end_position', 10))
    return JsonResponse({
            'status': '200',
            'message': '查询成功',
            'return_list': return_list[start_position: end_position]
        }, status=200)
    # except:
    #     return JsonResponse({
    #         'status': '400',
    #         'message': '查询错误'
    #     }, status=200)

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
    if not check_args_valid([task_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    if current_task.upload_user == current_user:
        return JsonResponse({
            'status': '400',
            'message': '自己不能接取自己的task'
        }, status=200)
    sid = transaction.savepoint()
    try:
        if current_task.task_status != 7:
            raise Exception
        current_task.sender_user = current_user
        cur_dialogue = start_task_dialogue(current_user, current_task.upload_user, current_task)
        if current_task.task_type == 1:
            cur_dialogue2 = start_task_dialogue(current_user, current_task.receive_user, current_task)
        current_task.dialogue_between_up_sender = cur_dialogue
        if current_task.task_type == 1:
            current_task.dialogue_between_re_sender = cur_dialogue2
        current_task.task_status = 1
        current_task.change_time = django.utils.timezone.now()
        current_task.save()
        if current_task.task_type == 1:
            current_tra = current_task.relation_transaction
            current_tra.has_task = True
            current_tra.save()
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
    if not check_args_valid([task_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    try:
        task_id = signer.unsign_object(task_id)
        current_task = task.models.Task.objects.get(id=task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'task不存在'
        }, status=200)
    if current_task.task_status != 1:
        return JsonResponse({
            'status': '400',
            'message': 'task状态错误'
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
        if current_task.task_type == 1:
            current_tra = current_task.relation_transaction
            current_tra.status = 3
            current_tra.send_time = django.utils.timezone.now()
            current_task.change_time = django.utils.timezone.now()
            current_tra.save()

    except:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}交予成功'.format(current_task.name))
    send_notice(current_task.upload_user.id,
                '您发布的任务{}物品被人领取，请确认'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '提交成功',
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
    if not check_args_valid([task_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
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
    if current_task.task_status != 2:
        return JsonResponse({
            'status': '400',
            'message': 'task状态错误'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_task.task_status = 3
        current_task.change_time = django.utils.timezone.now()
        current_task.save()
    except:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
    send_notice(current_user.id, '任务{}交予成功'.format(current_task.name))
    send_notice(current_task.upload_user.id,
                '您发布的任务{}物品被人送达，请确认'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '提交成功',
    }, status=200)


@transaction.atomic
@login_required(status=1)
def task_receive_object(request:HttpRequest):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    task_id = request.POST.get('task_id', None)
    if not task_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST错误'
        }, status=200)
    if not check_args_valid([task_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
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
    if current_task.task_status != 3:
        return JsonResponse({
            'status': '400',
            'message': 'task状态错误'
        }, status=200)
    sid = transaction.savepoint()
    try:
        current_task.task_status = 4
        current_task.save()
        current_task.sender_user.money += current_task.price
        current_task.change_time = django.utils.timezone.now()
        current_task.sender_user.save()
        if current_task.task_type == 1:
            current_tra = current_task.relation_transaction
            current_tra.status = 4
            current_tra.send_time = django.utils.timezone.now()
            current_tra.save()
    except:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
    send_notice(current_task.sender_user.id, '任务{}已经被确认收货'.format(current_task.name))
    send_notice(current_user.id,
                '您发布的任务{}以确认确认'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '提交成功',
    }, status=200)


@transaction.atomic
@login_required(status=1)
def task_comment(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    current_task_id = request.POST.get('task_id', None)
    comment_content = request.POST.get('comment_content', None)
    comment_level = int(request.POST.get('comment_level', None))
    if not all((current_task_id, comment_content, comment_level)):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    if not check_args_valid([current_task_id, comment_content, comment_level]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    signer = TimestampSigner()
    try:
        current_task_id = signer.unsign_object(current_task_id)
        current_task = task.models.Task.objects.get(id=current_task_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '任务异常',
        }, status=200)
    if current_task.task_status != 4:
        return JsonResponse({
            'status': '400',
            'message': '订单异常',
        }, status=200)
    if current_task.upload_user.id != current_user.id:
        return JsonResponse({
            'status': '400',
            'message': '不是你的订单',
        }, status=200)
    task_uploader = current_task.sender_user
    comment_target = current_task.sender_user

    sid = transaction.savepoint()
    try:
        current_task.task_status = 5
        current_task.change_time = django.utils.timezone.now()
        current_task.save()
        new_comment = user.models.CommentTask.objects.create(
            comment_content=comment_content,
            comment_user=current_user,
            comment_target=comment_target,
            comment_level=comment_level,
            comment_task=current_task,
        )
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
                '任务{}已被评价'.format(current_task.name))
    return JsonResponse({
        'status': '200',
        'message': '成功',
    }, status=200)


@login_required()
def task_wait_sender_list_up(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        upload_user=current_user).filter(task_status__exact=7)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_receive_object_list_up(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        upload_user=current_user).filter(task_status__exact=1)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_send_to_place_list_up(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        upload_user=current_user).filter(task_status__exact=2)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_confirm_receive_list_up(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        upload_user=current_user).filter(task_status__exact=3)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_confirm_comment_list_up(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        upload_user=current_user).filter(task_status__exact=4)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_confirm_success_list_up(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        upload_user=current_user).filter(task_status__exact=5)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_receive_object_list_sender(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        sender_user=current_user).filter(task_status__exact=1)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_send_to_place_list_sender(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        sender_user=current_user).filter(task_status__exact=2)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_confirm_receive_list_sender(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        sender_user=current_user).filter(task_status__exact=3)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_comment_list_sender(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        sender_user=current_user).filter(task_status__exact=4)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_wait_confirm_success_list_sender(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        sender_user=current_user).filter(task_status__exact=5)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def task_all_relative_list_receive(request):
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
    all_user_task_list = task.models.Task.objects.filter(
        receive_user=current_user).filter(task_status__exact=5)
    task_list = []
    for i in all_user_task_list.all():
        task_list.append(i.get_simple_info())
    if len(task_list) > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse({
        'status': '200',
        'message': '查询成功',
        'return_transaction': task_list[start_position: end_position],
        'has_next': str(has_next)
    }, status=200)


@login_required()
def transaction_relation_task(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    tra_id = request.POST.get('tra_id', None)
    if not tra_id:
        return JsonResponse({
        'status': '400',
        'message': 'POST字段不全',
    }, status=200)
    signer = TimestampSigner()
    try:
        tra_id = signer.unsign_object(tra_id)
        current_tra = order.models.Transaction.objects.get(id=tra_id)
        if not current_tra.has_task:
            return JsonResponse({
                'status': '400',
                'message': 'tra没有task',
            }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id错误',
        }, status=200)
    current_task = task.models.Task.objects.filter(relation_transaction=current_tra)
    if current_task:
        current_task = current_task.all()[0]
    else:
        return JsonResponse({
            'status': '400',
            'message': '系统错误',
        }, status=200)
    if current_task.task_status == 0:
        return JsonResponse({
            'status': '400',
            'message': 'task状态错误',
        }, status=200)
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'rela_task': current_task.get_simple_info()
    }, status=200)


@login_required()
def get_recommend_tasks(request):
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
    task_list = task.models.Task.objects.filter(task_status=7).order_by('-ddl_time')
    return_list = []
    for cur_task in task_list.all():
        return_list.append(cur_task.get_simple_info())
    has_next = False
    if len(return_list) > end_position:
        has_next = True
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'return_List': return_list[start_position:end_position],
        'has_next': has_next
    }, status=200)


@login_required()
def get_all_task_list_up(request):
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
    task_list = task.models.Task.objects.filter(upload_user=current_user).order_by('-change_time')
    return_list = []
    for cur_task in task_list.all():
        return_list.append(cur_task.get_simple_info())
    has_next = False
    if len(return_list) > end_position:
        has_next = True
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'return_List': return_list[start_position:end_position],
        'has_next': has_next
    }, status=200)


@login_required()
def get_all_task_list_tasker(request):
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
    task_list = task.models.Task.objects.filter(sender_user=current_user).order_by('-change_time')
    return_list = []
    for cur_task in task_list.all():
        return_list.append(cur_task.get_simple_info())
    has_next = False
    if len(return_list) > end_position:
        has_next = True
    return JsonResponse({
        'status': '200',
        'message': '成功',
        'return_List': return_list[start_position:end_position],
        'has_next': has_next
    }, status=200)

