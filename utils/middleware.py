from django import http
from django.utils.deprecation import MiddlewareMixin
from django_redis import get_redis_connection


def get_ip(request) -> str:
    real_ip = request.META.get('HTTP_X_REAL_IP', None)
    if not real_ip:
        real_ip = request.META.get('HTTP_REMOTE_USER_IP', None)
        if not real_ip:
            real_ip = request.META.get("REMOTE_ADDR", '127.0.0.1')
    print(f"Get IP: {real_ip}")
    return real_ip


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
            real_ip = get_ip(request)
            key = 'ip_{}_visit_num'.format(real_ip)
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