from ast import literal_eval

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
from utils.check_args_valid import *
from Final_Project1.settings import FILE_URL
# Create your views here.


file_url = FILE_URL


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
    if not check_args_valid([merchandise_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
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
    key2 = "today_view_num_{}".format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    key3 = "today_view_num_list_{}".format(django.utils.timezone.now().strftime('%Y-%m-%d'))
    today_view_num = conn.get(key2)
    if today_view_num:
        today_view_num = int(today_view_num)
        today_view_num += 1
    else:
        today_view_num = 0
    conn.set(key2, today_view_num)
    today_view_num_list = conn.get(key3)
    if today_view_num_list:
        today_view_num_list = literal_eval(today_view_num_list)
        today_view_num_list.append(django.utils.timezone.now().strftime('%Y-%m-%d %X'))
    else:
        today_view_num_list = []
        today_view_num_list.append(django.utils.timezone.now().strftime('%Y-%m-%d %X'))
    conn.set(key3, str(today_view_num_list))
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
        'mer_status': current_merchandise.status,
        'browsing': current_merchandise.browse_number,
        'fineness': current_merchandise.fineness,
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
        try:
            with open(info['path'], 'rb') as f:
                pass
        except:
            return JsonResponse({
                'status': '404',
                'message': '文件路径错误'
            }, status=200)
        # info['path'] = info['path'].replace('//', '/')
        return FileResponse(open(info['path'], 'rb'))
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
    if not check_args_valid([favorite_mer_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        favorite_mer_id = signer.unsign_object(favorite_mer_id)
        favorite_mer = commodity.models.Merchandise.objects.get(id=favorite_mer_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id解码异常'
        }, status=200)
    try:
        if favorite_mer.id in current_user.favorite_merchandise:
            return JsonResponse({
                'status': '300',
                'message': '不能重复收藏'
            }, status=200)
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
def favorite_merchandise_cancel_handler(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    favorite_mer_id = request.POST.get('mer_id', None)
    if not favorite_mer_id:
        return JsonResponse({
            'status': '300',
            'message': 'POST字段不全'
        }, status=200)
    if not check_args_valid([favorite_mer_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        favorite_mer_id = signer.unsign_object(favorite_mer_id)
        favorite_mer = commodity.models.Merchandise.objects.get(id=favorite_mer_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id解码异常'
        }, status=200)
    try:
        if favorite_mer.id not in current_user.favorite_merchandise:
            return JsonResponse({
                'status': '300',
                'message': '不在收藏列表中'
            }, status=200)
        current_user.favorite_merchandise.remove(favorite_mer.id)
        current_user.save()
        favorite_mer.who_favourite.remove(current_user.id)
        favorite_mer.save()
        return JsonResponse({
            'status': '200',
            'message': '删除成功'
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
    if not check_args_valid([favorite_bus_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        signer = TimestampSigner()
        favorite_bus_id = signer.unsign_object(favorite_bus_id)
        mer_upload_user = user.models.User.objects.get(id=favorite_bus_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id解码异常'
        }, status=200)
    if mer_upload_user == current_user:
        return JsonResponse({
            'status': '300',
            'message': '自己不能收藏自己'
        }, status=200)
    try:
        if mer_upload_user.id in current_user.favorite_sellers:
            return JsonResponse({
                'status': '300',
                'message': '不能重复收藏'
            }, status=200)
        current_user.favorite_sellers.append(mer_upload_user.id)
        current_user.save()
        mer_upload_user.as_favorite_business_number += 1
        mer_upload_user.save()
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
def favorite_business_cancel_handler(request):
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    signer = TimestampSigner()
    favorite_bus_id = request.POST.get('favorite_bus_id', None)
    if not favorite_bus_id:
        return JsonResponse({
            'status': '300',
            'message': 'POST字段不全'
        }, status=200)
    if not check_args_valid([favorite_bus_id]):
        return JsonResponse({
            'status': '400',
            'message': 'POST字段错误'
        })
    try:
        signer = TimestampSigner()
        favorite_bus_id = signer.unsign_object(favorite_bus_id)
        mer_upload_user = user.models.User.objects.get(id=favorite_bus_id)
    except:
        return JsonResponse({
            'status': '300',
            'message': 'id解码异常'
        }, status=200)
    try:
        if mer_upload_user.id not in current_user.favorite_sellers:
            return JsonResponse({
                'status': '300',
                'message': '不在收藏列表'
            }, status=200)
        current_user.favorite_sellers.remove(mer_upload_user.id)
        current_user.save()
        mer_upload_user.as_favorite_business_number -= 1
        mer_upload_user.save()
        return JsonResponse({
            'status': '200',
            'message': '删除成功'
        }, status=200)
    except:
        return JsonResponse({
            'status': '300',
            'message': '删除异常'
        }, status=200)



@login_required()
def search_by_class_label_all(request):
    method_list = ["new", "hot", "price", 'default', "-new", "-hot", "-price"]
    fineness_list = [1, 2, 3, 4]
    current_user = user.models.User.objects.get(id=request.session.get('user_id'))
    class1_id = request.POST.get('class1_id', None)
    class2_id = request.POST.get('class2_id', None)
    sort_method = request.POST.get('sort_method', 'default')
    fineness_id = request.POST.get('fineness_id', None)
    search_str = request.POST.get('search_str', None)
    start_position = request.POST.get('start_position', 0)
    end_position = request.POST.get('end_position', 30)
    try:
        start_position = int(start_position)
        end_position = int(end_position)
    except:
        return JsonResponse({
            'status': '400',
            'message': 'POST字段异常',
        }, status=200)
    if (not class1_id and not search_str) or (sort_method not in method_list):
        return JsonResponse({
            'status': '400',
            'message': '字段值错误'
        }, status=200)
    if fineness_id:
        if int(fineness_id) not in fineness_list:
            return JsonResponse({
                'status': '400',
                'message': '字段值错误'
            }, status=200)
    try:
        if class1_id:
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

        else:
            mer_list = commodity.models.Merchandise.objects.filter(status__exact=1).filter(Q(name__contains=search_str) |Q(description__contains=search_str)
                                           | Q(class_level_1__name_str__contains=search_str)
                                           | Q(class_level_2__name_str__contains=search_str))
            if sort_method:
                if sort_method == 'new':
                    order_by = ('-upload_date',)
                elif sort_method == 'hot':
                    order_by = ('-favourite_number',)
                elif sort_method == 'price':
                    order_by = ('price',)
                elif sort_method == '-new':
                    order_by = ('upload_date',)
                elif sort_method == '-hot':
                    order_by = ('favourite_number',)
                elif sort_method == '-price':
                    order_by = ('-price',)
                else:
                    order_by = ('-pk',)  # 按照primary key降序排列。
                mer_list = mer_list.order_by(*order_by)

        return_list = []
        for i in mer_list.all():
            return_list.append(i.get_simple_info())
        has_next = False
        if len(return_list) > end_position:
            has_next = True
        return JsonResponse({
                'status': '200',
                'message': '查询成功',
                'return_list': return_list[start_position: end_position],
                'has_next': has_next,
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





