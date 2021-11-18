from functools import wraps

from django.http import JsonResponse, HttpResponse
import user.models


def login_required(status=0, callback=None, method='POST'):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            if request.method == method:
                a = request.session.get('is_login', None)
                if not request.session.get('is_login', False):
                    return JsonResponse({
                        'status': '404',
                        'message': 'User not login '
                    }, status=407)
                try:
                    user_id = request.session['user_id']
                except:
                    return JsonResponse({
                        'status': '500',
                        'message': 'cookie 错误， 请清空cookie'
                    }, status=200)
                try:
                    current_user = user.models.User.objects.get(id=user_id)
                    if current_user.user_status < status:
                        return JsonResponse({
                            'status': '500',
                            'message': '用户无权访问'
                        }, status=407)
                except:
                    return JsonResponse({
                        'status': '300',
                        'message': '请求详细信息用户不存在'
                    }, status=200)
            else:
                return HttpResponse(status=500)
            return fn(request, *args, **kw)
        return _wrapped

    return decorator