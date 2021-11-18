import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.utils import *
import django.utils.timezone


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = None
        self.room_group_name = None
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        token = self.scope['url_route']['kwargs']['room_name']
        # signer = TimestampSigner()
        # token = signer.unsign_object(token)
        return_dict = get_user_id_by_token(token) #通过token获取userID
        if not return_dict['status']:
            self.close()
        else:
            user_id = return_dict['user_id']
            set_user_online(user_id)
            self.room_group_name = 'chat_{}'.format(user_id)
            self.user_id = user_id
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
            conn = get_redis_connection('default')
            key = 'online_num_{}'.format(django.utils.timezone.now().strftime('%Y-%m-%d'))
            online_number = conn.get(key)
            if online_number:
                online_number = int(online_number)
                online_number += 1
            else:
                online_number = 0
            conn.set(key, online_number)

    def disconnect(self, close_code):
        # Leave room group
        if self.user_id:
            set_user_outline(self.user_id)
        if self.room_group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    def receive(self, text_data):
        signer = TimestampSigner()
        text_data_json = json.loads(text_data)
        user_id = self.user_id
        dialogue_id = text_data_json.get('dialogue_id', None)
        info = text_data_json.get('info', None)
        data_type = text_data_json.get('data_type', None)
        if not all((user_id, dialogue_id, info, data_type)): #判断字段是否齐全
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': dict({
                        'message': '传入数据字段不全',
                        'status': 0
                    })
                }
            )
        else:
            if not has_order_to_send(user_id, dialogue_id):
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': dict({
                            'message': '无权发送',
                            'status': 0
                        })
                    }
                )
            else:
                return_dict = add_info_to_dialogue(user_id, dialogue_id, info, data_type)
                if not return_dict['status']:
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': dict({
                                'message': '异常错误',
                                'status': 0
                            })
                        }
                    )
                else:
                    target_id = return_dict['return_id']
                    if is_user_online(target_id):
                        send_message = dict(
                            {
                                'type': 'chat_message',
                                'message': {
                                        'message': '成功',
                                        'status': 1,
                                        'info': info,
                                        'dialogue_id': signer.sign_object(dialogue_id),
                                        'from_id': signer.sign_object(user_id),
                                        'to': signer.sign_object(target_id),
                                        'data_type': data_type,
                                            },
                            }
                        )
                        send_message_user(target_id, send_message)

                    # Send message to room group
                    des_group = "chat_{}".format(user_id)
                    async_to_sync(self.channel_layer.group_send)(
                        des_group,
                        {
                            'type': 'chat_message',
                            'message': dict({
                                    'message': '发送成功',
                                    'status': 2,
                                    'info': info,
                                    'from': signer.sign_object(user_id),
                                    'to': signer.sign_object(target_id),
                                    'data_type': data_type,
                                    'dialogue_id': signer.sign_object(dialogue_id),
                                })
                        }
                    )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'info': message
        }))