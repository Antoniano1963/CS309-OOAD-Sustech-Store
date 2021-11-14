from django import http
from django.utils.deprecation import MiddlewareMixin
from django_redis import get_redis_connection


class BlockedIpMiddlewareID(MiddlewareMixin):
    def process_request(self, request):
        try:
            user_id = request.session.get('user_id', None)
            if not user_id:
                pass
            else:
                conn = get_redis_connection('default')
                key = 'user_{}_visit_num'.format(user_id)
                visit_num = conn.get(key)
                if visit_num:
                    visit_num = int(visit_num) + 1
                    conn.set(key, visit_num, 20)
                    if visit_num >= 20:
                        conn.set(key, visit_num, 300)
                        return http.HttpResponseForbidden('<h1>Forbidden</h1>')
                else:
                    visit_num = 1
                    conn.set(key, visit_num, 20)
        except:
            pass


class BlockedIpMiddlewareIP(MiddlewareMixin):
    def process_request(self, request):
        try:
            key = 'ip_{}_visit_num'.format(request.META['REMOTE_ADDR'])
            conn = get_redis_connection('default')
            visit_num = conn.get(key)
            if visit_num:
                visit_num = int(visit_num) + 1
                conn.set(key, visit_num, 20)
                if visit_num >= 200:
                    conn.set(key, visit_num, 300)
                    return http.HttpResponseForbidden('<h1>Forbidden</h1>')
                else:
                    pass
            else:
                visit_num = 1
                conn.set(key, visit_num, 20)
        except:
            pass