from ast import literal_eval
from django.core.signing import TimestampSigner
from django_redis import get_redis_connection
import task.models

def start_task_dialogue(sender, user0, task:task.models.Task.objects):
    import user.models
    import task.models
    import dialogue.models
    new_dialogue = dialogue.models.Dialogue.objects.create(
        dialogue_user1=user0,
        dialogue_user2=sender,
        dialogue_type=2
    )
    new_dialogue.save()
    conn = get_redis_connection('default')
    conn.set('dialogue_{}'.format(new_dialogue.id), str([new_dialogue.dialogue_user1.id,
                                                                      new_dialogue.dialogue_user2.id]))
    # order_list_u = conn.get("session_{}".format(new_dialogue.dialogue_user.id))
    # if not order_list_u:
    #     order_list_u = []
    # else:
    #     order_list_u = literal_eval(order_list_u)
    # order_list_u.append(new_dialssion_{}".format(new_dialogue.dialogue_business.id))
    # if not order_list_b:ogue.id)
    #     # order_list_b = conn.get("se
    #     order_list_b = []
    # else:
    #     order_list_b = conn(order_list_b)
    # order_list_b.append(new_dialogue.id)
    # conn.set("session_{}".format(new_dialogue.dialogue_user.id), str(order_list_u))
    # conn.set("session_{}".format(new_dialogue.dialogue_business.id), str(order_list_b))
    # new_dialogue.dialogue_user_key = "session_{}".format(new_dialogue.dialogue_user.id)
    # new_dialogue.dialogue_business_key = "session_{}".format(new_dialogue.dialogue_business.id)
    return new_dialogue