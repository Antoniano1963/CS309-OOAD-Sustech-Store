from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
import channels.layers
from asgiref.sync import async_to_sync
from django_redis import get_redis_connection
from redis import Redis
from ast import literal_eval
import django.utils.timezone
from django.core.signing import TimestampSigner
from Final_Project1.celery import send_active_email




def send_message_user(user_id, message, from_user_id = -1):
    #向user_id发送消息
    web_channels = channels.layers.get_channel_layer()
    # async_to_sync(web_channels.group_send)(
    #     'chat_{}'.format(user_id),
    #     {
    #         'type': 'chat_message',
    #         'message': dict({
    #             'message': '成功',
    #             'status': 0,
    #             'info': message,
    #             'session_id': -1,
    #             'from_id': from_user_id,
    #             'to': None,
    #         },
    #         ),
    #     }
    # )
    async_to_sync(web_channels.group_send)(
        'chat_{}'.format(user_id),
        message
    )
    return True


def has_order_to_send(user_id, dialogue_id):
    redis_connect = get_redis_connection('default')
    signer = TimestampSigner()
    dialogue_id = signer.unsign_object(dialogue_id)
    order_list = redis_connect.get("dialogue_{}".format(dialogue_id))
    # order_list = redis_connect.get("session_{}".format(user_id))
    if not order_list:
        return False
    order_list = literal_eval(order_list)
    if int(user_id) in order_list:
        return True
    return False


def is_user_online(user_id):
    redis_connect = get_redis_connection('default')
    is_online = redis_connect.get('is_online_{}'.format(user_id))
    if not is_online:
        return False
    if is_online == str(False):
        return False
    return True


def set_user_outline(user_id):
    redis_connect = get_redis_connection('default')
    redis_connect.set('is_online_{}'.format(user_id), str(False))


def set_user_online(user_id):
    redis_connect = get_redis_connection('default')
    redis_connect.set('is_online_{}'.format(user_id), str(True))


def add_info_to_dialogue(user_id, dialogue_id, message, data_type=1):
    #这里的user_id是发送消息的人
    signer = TimestampSigner()
    dialogue_id = signer.unsign_object(dialogue_id)
    try:
        import dialogue.models
        current_dialogue = dialogue.models.Dialogue.objects.get(id=dialogue_id)
    except:
        return dict({
            'status': False
        })
    if user_id == str(current_dialogue.dialogue_user1.id):
        current_dialogue.user2_wait_message_number += 1
        return_id = current_dialogue.dialogue_user2.id
        my_name = current_dialogue.dialogue_user1.name
        other_name = current_dialogue.dialogue_user2.name
    else:
        current_dialogue.user1_wait_message_number += 1
        return_id = current_dialogue.dialogue_user1.id
        other_name = current_dialogue.dialogue_user1.name
        my_name = current_dialogue.dialogue_user2.name

    try:
        current_dialogue.dialogue_info.append(
            dict({
                'date': django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'information': message,
                'which_say': user_id,
                'data_type': data_type,
                'my_name': my_name,
                'other_name': other_name,
            })
        )
        current_dialogue.update_date = django.utils.timezone.now()
        current_dialogue.save()
        return dict({
            'status': True,
            'return_id': return_id,
            'my_name': my_name,
            'other_name':other_name,
        })
    except:
        return dict({
            'status': False
        })


def get_user_id_by_token(token):
    redis_connect = get_redis_connection('default')
    user_id = redis_connect.get(token)
    if user_id:
        redis_connect.delete(token) #注意建立连接后会删除token
        return dict({
            'status': True,
            'user_id': user_id
        })
    return dict({
        'status': False
    })


def add_token_relationship(user_id, token):
    redis_connect = get_redis_connection('default')
    redis_connect.set(token, user_id)


def send_notice(user_id, message):
    import user.models
    current_user = user.models.User.objects.get(id=user_id)
    signer = TimestampSigner()
    current_user.notice_info_unread.append(
        dict({
            'date': django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'information': message,
            'which_say': 'office'
        })
    )
    current_user.wait_notice += 1
    current_user.save()
    dict_message = dict(
        {
            'type': 'chat_message',
            'message': {
                    'message': '成功',
                    'status': 1,
                    'info': message,
                    'session_id': -1,
                    'from_id': -1,
                    'to': signer.sign_object(current_user.id),
                    'data_type': 1,
                        },
        }
    )
    if is_user_online(user_id):
        send_message_user(user_id, dict_message)
    send_active_email.delay(message, 'a', current_user.email, type=2)