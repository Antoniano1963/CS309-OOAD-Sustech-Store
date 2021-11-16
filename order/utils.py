from django_redis import get_redis_connection

import commodity.models

def server_cart_del(mer_id, user_id):
    conn = get_redis_connection('default')
    cart_key = 'cart_{}'.format(user_id)
    conn.hdel(cart_key, mer_id)