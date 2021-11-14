from django.core.signing import TimestampSigner
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse, HttpRequest
from datetime import datetime
import hashlib
import sys
import django.utils.timezone
from django_redis import get_redis_connection
from haystack.views import SearchView

import commodity.models
import user.models
import order.models
from utils import myemail_sender, random_utils
from Final_Project1.decotators.login_required import login_required
# Create your views here.


file_url = "http://store.sustech.xyz:8080/api/commodity/download/?key="


@login_required()
def commodity_detail(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    merchandise_id = request.POST.get('mer_id', None)
    if not merchandise_id:
        return JsonResponse({
            'status': '400',
            'message': 'POST信息不全'
        }, status=200)
    merchandise_id = signer.unsign_object(merchandise_id)
    try:
        current_merchandise = commodity.models.Merchandise.objects.get(id=merchandise_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': '请求详细信息用户不存在'
        }, status=200)
    current_merchandise.browse_number += 1
    current_merchandise.save()
    mer_image_url1 = current_merchandise.get_avatar_url1().replace('/', '\\')
    mer_image_url2 = current_merchandise.get_avatar_url2().replace('/', '\\')
    mer_image_url3 = current_merchandise.get_avatar_url3().replace('/', '\\')
    img_num = 1
    if current_merchandise.image2:
        img_num += 1
    if current_merchandise.image3:
        img_num += 1
    info1 = dict({
        'mer_id': current_merchandise.id,
        'date': str(django.utils.timezone.now()),
        'path': mer_image_url1
    })
    info2 = dict({
        'mer_id': current_merchandise.id,
        'date': str(django.utils.timezone.now()),
        'path': mer_image_url2
    })
    info3 = dict({
        'mer_id': current_merchandise.id,
        'date': str(django.utils.timezone.now()),
        'path': mer_image_url3
    })
    signer = TimestampSigner()
    conn = get_redis_connection('default')
    key = 'history_{}'.format(current_user.id)
    conn.lrem(key, 0, current_merchandise.id)
    conn.lpush(key, current_merchandise.id)
    # 保存用户最近浏览的20个商品
    conn.ltrim(key, 0, 19)
    return JsonResponse({
        'status': '200',
        'message': '成功返回商品{}的信息'.format(current_merchandise.name),
        'mer_id': signer.sign_object(current_merchandise.id),
        'mer_name': current_merchandise.name,
        'mer_update': current_merchandise.upload_date,
        'mer_price': str(current_merchandise.price),
        'mer_deliver_price': current_merchandise.deliver_price,
        'mer_upload_user_id': signer.sign_object(current_merchandise.upload_user.id),
        'mer_upload_user_name': current_merchandise.upload_user.name,
        'mer_description': current_merchandise.description,
        'mer_image1_url': f"{file_url}{signer.sign_object(info1)}",
        'mer_image2_url': f"{file_url}{signer.sign_object(info2)}",
        'mer_image3_url': f"{file_url}{signer.sign_object(info3)}",
        'img_num': str(img_num),
        'addr_info': current_merchandise.sender_addr.get_basic_info(),
        'class_level_1': current_merchandise.class_level_1.name,
        'class_level_2': current_merchandise.class_level_2.name,
        'allow_face_trade': current_merchandise.allow_face_trade,
        'as_favorite_number': len(current_merchandise.who_favourite),
    }, status=200)


# @login_required(method='GET')
def download_handler(request):
    if request.method == 'GET':
        # if not request.session.get('is_login', False):
        #     return JsonResponse({
        #         'status': '404',
        #         'message': 'User not login '
        #     }, status=403)
        # try:
        #     user_id = request.session['user_id']
        # except:
        #     return JsonResponse({
        #         'status': '500',
        #         'message': 'cookie 错误， 请清空cookie'
        #     }, status=403)
        # try:
        #     current_user = login.models.User.objects.get(id=user_id)
        # except:
        #     return JsonResponse({
        #         'status': '300',
        #         'message': '请求详细信息用户不存在'
        #     }, status=200)
        info = request.GET.get('key', None)
        if not info:
            return JsonResponse({
                'status': '403',
                'message': 'key错误'
            }, status=403)
        # try:
        signer = TimestampSigner()
        info = signer.unsign_object(info)
        # path = info['path']
        info['path'] = info['path'].replace('\\', '/')
        # info['path'] = info['path'].replace('//', '/')
        return FileResponse(open(info['path'], 'rb'))
        # except:
        #     return JsonResponse({
        #         'status': '500',
        #         'message': '解码错误'
        #     }, status=403)
    return HttpResponse(status=500)


@login_required()
def add_favorite_merchandise_handler(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    favorite_mer_id = request.POST.get('mer_id', None)
    if not favorite_mer_id:
        return JsonResponse({
            'status': '300',
            'message': 'POST字段不全'
        }, status=200)
    try:
        favorite_mer_id = signer.unsign_object(favorite_mer_id)
        favorite_mer = commodity.models.Merchandise.objects.get(favorite_mer_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id解码异常'
        }, status=200)
    try:
        current_user.favorite_merchandise.append(favorite_mer_id)
        current_user.save()
        favorite_mer.who_favourite.append(current_user.id)
        favorite_mer.save()
        return JsonResponse({
            'status': '200',
            'message': '收藏成功'
        }, status=200)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id添加异常'
        }, status=200)


@login_required()
def add_favorite_business_handler(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    favorite_bus_id = request.POST.get('mer_upload_user_id', None)
    if not favorite_bus_id:
        return JsonResponse({
            'status': '300',
            'message': 'POST字段不全'
        }, status=200)
    try:
        signer = TimestampSigner()
        favorite_bus_id = signer.unsign_object(favorite_bus_id)
        if int(favorite_bus_id) == current_user.id:
            return JsonResponse({
            'status': '400',
            'message': '自己不能收藏自己'
        }, status=200)

        mer_upload_user = user.models.User.objects.get(id=favorite_bus_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id解码异常'
        }, status=200)
    # try:
    current_user.favorite_sellers.append(mer_upload_user.id)
    current_user.save()
    mer_upload_user.as_favorite_business_number += 1
    mer_upload_user.save()
    return JsonResponse({
        'status': '200',
        'message': '收藏成功'
    }, status=200)
    # except:
    #     return JsonResponse({
    #         'status': '300',
    #         'message': 'id添加异常'
    #     }, status=200)



@login_required()
def search_by_class_label_all(request: HttpRequest):
    method_list = ["new", "hot", "price", 'default']
    fineness_list = [1, 2, 3, 4]
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    class1_id = request.POST.get('class1_id', None)
    class2_id = request.POST.get('class2_id', None)
    sort_method = request.POST.get('sort_method', 'default')
    fineness_id = request.POST.get('fineness_id', None)
    search_str = request.POST.get('search_str', None)
    if not class1_id or sort_method not in method_list:
        return JsonResponse({
            'status': '400',
            'message': '字段值错误'
        }, status=200)
    if fineness_id:
        if fineness_id not in fineness_list:
            return JsonResponse({
                'status': '400',
                'message': '字段值错误'
            }, status=200)
    try:
        if class2_id:
            mer_list = commodity.models.Merchandise.objects.get_merchandises_by_class(
                class1_id=class1_id, class2_id=class2_id, fineness_id=fineness_id, sort=sort_method)
        else:
            mer_list = commodity.models.Merchandise.objects.get_merchandises_only_by_class1(
                class1_id=class1_id, fineness_id=fineness_id, sort=sort_method)
        if search_str:
            mer_list = mer_list.filter(Q(name__contains=search_str) |Q(description__contains=search_str)
                                       | Q(class_level_1__name_str__contains=search_str)
                                       | Q(class_level_2__name_str__contains=search_str))
        return_list = []
        for i in mer_list.all():
            return_list.append(i.get_simple_info())
        start_position = int(request.POST.get('start_position', 0))
        end_position = int(request.POST.get('end_position', 10))
        return JsonResponse({
                'status': '200',
                'message': '查询成功',
                'return_list': return_list[start_position: end_position]
            }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '查询错误'
        }, status=200)


@login_required()
def history_browsing_mer(request:HttpRequest):
    try:
        start_position = request.POST.get('start_position', 0)
        end_position = request.POST.get('end_position', 19)
        current_user = user.models.User.objects.get(id=request.session.get('user_id'))
        conn = get_redis_connection('default')
        key = 'history_{}'.format(current_user.id)
        history_li = conn.lrange(key, start_position, end_position)
        return_list = []
        for id in history_li:
            return_list.append(commodity.models.Merchandise.objects.get(id=id).get_simple_info())
        has_next = True if end_position < 19 else False
        return JsonResponse({
                'status': '200',
                'message': '查询成功',
                'return_list': return_list,
                'has_next': has_next
            }, status=200)
    except:
        return JsonResponse({
            'status': '400',
            'message': '查询错误'
        }, status=200)


    # python manage.py rebuild_index
class MysearchView(SearchView):
    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        context = super().get_context()
        keyword = self.request.GET.get('q', None)  # 关键子为q
        if not keyword:
            return JsonResponse({'message': '没有相关信息'})
        else:
            print(keyword)
            print(context)
            return_list = []
            for i in context['page'].object_list:
                if i.object.status == 1:
                    return_list.append(i.object.get_simple_info())
            return JsonResponse({'message': keyword,
                                 'return_list': return_list})





