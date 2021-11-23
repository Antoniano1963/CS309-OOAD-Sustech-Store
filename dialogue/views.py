import math
import os

import django.utils.timezone
from PIL import Image
from django.http import JsonResponse
from django_redis import get_redis_connection
import user.models
import dialogue.models
from Final_Project1.settings import MEDIA_ROOT
from utils import myemail_sender, random_utils
from django.core.signing import TimestampSigner
from Final_Project1.decotators.login_required import login_required
from ast import literal_eval
from chat.utils import add_token_relationship
from django.db.models import Q
from chat.utils import is_user_online
import re

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.shortcuts import render
# from login.tasks import send_active_email

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
from utils import myemail_sender, random_utils
from Final_Project1.decotators.login_required import login_required
from django.db import transaction
from chat.utils import *
from Final_Project1.settings import FILE_URL
# Create your views here.


@login_required()
def start_dialogue(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    user2_id = request.POST.get('business_id', None)
    signer = TimestampSigner()
    if not user2_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全'
        }, status=200)
    try:
        user2_id = signer.unsign_object(user2_id)
        current_user2 = user.models.User.objects.get(id=user2_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '用户不存在'
        }, status=200)
    current_dialogue1 = None
    current_dialogue2 = None
    try:
        current_dialogue1 = dialogue.models.Dialogue.objects.filter(dialogue_type__exact=1).filter(
            dialogue_user1=current_user).filter(dialogue_user2=current_user2)

        # except:
        #     pass
        # try:
        current_dialogue2 = dialogue.models.Dialogue.objects.filter(dialogue_type__exact=1).filter(
        dialogue_user2=current_user).filter(dialogue_user1=current_user2)
        # except:
        #     pass
        current_dialogue = None
        if current_dialogue1:
            current_dialogue = current_dialogue1.all()[0]
        if current_dialogue2:
            current_dialogue = current_dialogue2.all()[0]
        if current_dialogue:
            redis_connect = get_redis_connection('default')
            redis_connect.set('dialogue_{}'.format(current_dialogue.id), str([current_dialogue.dialogue_user1.id,
                                                                          current_dialogue.dialogue_user2.id]))
            # order_list_u = redis_connect.get("session_{}".format(current_dialogue.dialogue_user.id))
            # if not order_list_u:
            #     order_list_u = []
            # else:
            #     order_list_u = literal_eval(order_list_u)
            # if current_dialogue.id not in order_list_u:
            #     order_list_u.append(current_dialogue.id)
            # order_list_b = redis_connect.get("session_{}".format(current_dialogue.dialogue_business.id))
            # if not order_list_b:
            #     order_list_b = []
            # else:
            #     order_list_b = literal_eval(order_list_b)
            # if current_dialogue.id not in order_list_b:
            #     order_list_b.append(current_dialogue.id)
            # redis_connect.set("session_{}".format(current_dialogue.dialogue_user.id), str(order_list_u))
            # redis_connect.set("session_{}".format(current_dialogue.dialogue_business.id), str(order_list_b))
            return JsonResponse({
                'status': '201',
                'message': '对话已存在',
                'dialogue_id': signer.sign_object(current_dialogue.id)
            }, status=200)
        else:
            new_dialogue = dialogue.models.Dialogue.objects.create(
                dialogue_user1=current_user,
                dialogue_user2=current_user2,
                # dialogue_merchandise_id=merchandise_id
            )
            new_dialogue.save()
            redis_connect = get_redis_connection('default')
            redis_connect.set('dialogue_{}'.format(new_dialogue.id), str([new_dialogue.dialogue_user1.id,
                                                                              new_dialogue.dialogue_user2.id]))
            # order_list_u = redis_connect.get("session_{}".format(new_dialogue.dialogue_user.id))
            # if not order_list_u:
            #     order_list_u = []
            # else:
            #     order_list_u = literal_eval(order_list_u)
            # order_list_u.append(new_dialogue.id)
            # order_list_b = redis_connect.get("session_{}".format(new_dialogue.dialogue_business.id))
            # if not order_list_b:
            #     order_list_b = []
            # else:
            #     order_list_b = literal_eval(order_list_b)
            # order_list_b.append(new_dialogue.id)
            # redis_connect.set("session_{}".format(new_dialogue.dialogue_business.id), str(order_list_u))
            # redis_connect.set("session_{}".format(new_dialogue.dialogue_business.id), str(order_list_b))
            return JsonResponse({
                'status': '200',
                'message': '对话创建成功',
                'dialogue_id': signer.sign_object(new_dialogue.id)
            }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id错误，创建失败'
        }, status=200)


@login_required()
def dialogue_detail(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    dialogue_id = request.POST.get('dialogue_id', None)
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 10)
    if not dialogue_id:
        return JsonResponse({
            'status': '301',
            'message': 'POST缺少字段'
        }, status=200)
    try:
        dialogue_id = signer.unsign_object(dialogue_id)
        current_dialogue = dialogue.models.Dialogue.objects.get(id=dialogue_id)
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'id解码错误'
        }, status=200)
    try:
        info_list = current_dialogue.dialogue_info
        info_list.sort(key=lambda x: x["date"])
        info_list.reverse()
        info_list_len = len(info_list)
        return_list = []
        current_user_wait_number = 0
        if current_user.id == current_dialogue.dialogue_user1.id:
            current_user_wait_number = current_dialogue.user1_wait_message_number
            current_dialogue.user1_wait_message_number = 0
        else:
            current_user_wait_number = current_dialogue.user2_wait_message_number
            current_dialogue.user2_wait_message_number = 0
        current_dialogue.save()
        end_position = max(end_position, current_user_wait_number+5)
        if info_list_len > end_position:
            has_next = True
        else:
            has_next = False
        for info in info_list:
            if int(info['which_say']) == current_user.id:
                info['which_say'] = 0
            else:
                info['which_say'] = signer.sign_object(info['which_say'])
        return JsonResponse(dict({
            'dialogue_user1_id': signer.sign_object(current_dialogue.dialogue_user1.id),
            'dialogue_user2_id': signer.sign_object(current_dialogue.dialogue_user2.id),
            'dialogue_user1_name': current_dialogue.dialogue_user1.name,
            'dialogue_user2_name': current_dialogue.dialogue_user2.name,
            'dialogue_info': info_list[start_position:end_position],
            'wait_number': current_user_wait_number,
            'dialogue_type': current_dialogue.dialogue_type,
            'has_next': has_next,

        }))
    except:
        return JsonResponse({
            'status': '400',
            'message': '目标id不存在'
        }, status=200)
@login_required()
def dialogue_list(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    start_position = int(request.POST.get('start_position', 0))
    end_position = int(request.POST.get('end_position', 10))
    dialogues_List = dialogue.models.Dialogue.objects.filter(dialogue_type=1).filter(
        Q(dialogue_user1=current_user) |Q(dialogue_user2=current_user)).order_by('update_date').all().reverse()
    return_dia_list = []
    signer = TimestampSigner()
    for dia in dialogues_List:
        return_dia_list.append({
            'dialogue_id': signer.sign_object(dia.id),
            'user1_id': signer.sign_object(dia.dialogue_user1.id),
            'user2_id': signer.sign_object(dia.dialogue_user2.id),
            'user1_name': dia.dialogue_user1.name,
            'user2_name': dia.dialogue_user2.name,
            'last_info': dia.dialogue_info[-1] if len(dia.dialogue_info) > 0 else None,
            'update_time': str(dia.update_date),
            'wait_number': dia.user1_wait_message_number if current_user == dia.dialogue_user1 else dia.user2_wait_message_number,
            'dialogue_type': dia.dialogue_type,
        })
    for info in return_dia_list:
        if info['last_info']:
            info['last_info']['which_say'] = signer.sign_object(info['last_info']['which_say'])
    dia_list_len = len(return_dia_list)
    if dia_list_len > end_position:
        has_next = True
    else:
        has_next = False
    return JsonResponse(dict({
        'message': '成功',
        'status': "200",
        'return_list': return_dia_list[start_position:end_position],
        'has_next': has_next,
    }))


@login_required()
def begin_websocket(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    # if is_user_online(current_user.id):
    #     return JsonResponse({
    #         'status': '400',
    #         'message': 'User已经开启一个websocket了',
    #     }, status=200)

    code = random_utils.random_str(18, 'upper_str')
    add_token_relationship(current_user.id, code)
    return JsonResponse({
            'status': '200',
            'message': '成功',
            'token': code
        }, status=200)


file_url = FILE_URL
@login_required()
def receive_img(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    dialogue_id = request.POST.get('dialogue_id', None)
    signer = TimestampSigner()
    if not dialogue_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段不全',
        }, status=200)
    try:
        dialogue_id = signer.unsign_object(dialogue_id)
        image1 = request.FILES['image1']
        current_dialogue = dialogue.models.Dialogue.objects.get(id=dialogue_id)
    except:
        return JsonResponse({
            'status': '400',
            'message': '图片错误',
        }, status=200)
    if current_user != current_dialogue.dialogue_user1 and current_user != current_dialogue.dialogue_user2:
        return JsonResponse({
            'status': '400',
            'message': '不是你的对话',
        }, status=200)
    try:
        reopen_img1 = Image.open(image1)
        reopen_img1.thumbnail((200, 100), Image.ANTIALIAS)
        img_path = os.path.join(MEDIA_ROOT, 'dialogue_{0}/user_{1}_dia/{2}'.format(
            dialogue_id, current_user.id, 'dialogue_{1}.png'.format(current_dialogue.id, current_dialogue.image_number)))
        img_path3 = os.path.join(MEDIA_ROOT, 'dialogue_{0}/user_{1}_dia/'.format(
            dialogue_id, current_user.id, ))
        isExists = os.path.exists(img_path3)
        if not isExists:
            os.makedirs(img_path3)
        with open(img_path, 'wb+') as f:
            reopen_img1.save(f, format='PNG')
        info = dict({
            'dia_id': current_dialogue.id,
            'date': str(django.utils.timezone.now()),
            'path': img_path
        })
        signer = TimestampSigner()
        current_dialogue.image_number += 1
        current_dialogue.save()
    except:
        return JsonResponse({
            'status': '400',
            'message': '图片错误',
        }, status=200)
    return JsonResponse({
            'status': '200',
            'message': '成功',
            'dia_img_url': f"{file_url}{signer.sign_object(info)}",
        }, status=200)