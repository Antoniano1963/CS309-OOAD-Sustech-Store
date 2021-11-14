# bookstore/celery.py
import datetime
import os
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone
from django_redis import get_redis_connection
from redis import Redis
from celery import Celery
from .settings import EMAIL_FROM

import django.utils.timezone

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Final_Project1.settings')

app = Celery('Final_Project1', broker='redis://127.0.0.1:6379/6')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.now = timezone.now


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, cancel_non_pay_tra.s(), name='cancel non-pay transactions every 60 seconds')
    sender.add_periodic_task(60.0, create_matrix.s(), name='create recommend matrix every 60 seconds')
    # sender.add_periodic_task(10.0, test_fuc2.s(), name='sync statistic_info every 10 seconds')


@app.task(name = 'send_email', time_limit=15)
def send_active_email(code, username, email, subject='0.0', type=2):
    '''发送激活邮件'''
    subject = '0.0' # 标题
    message = ''
    sender = EMAIL_FROM # 发件人
    receiver = [email] # 收件人列表
    html_message1 = '<div>Code is {}</div>'.format(code)
    html_message2 = '<div>通知消息为 is {}</div>'.format(code)
    html_message = html_message1 if type ==1 else html_message2
    print(code)
    send_mail(subject, message, sender, receiver, html_message=html_message)


@app.task(name = 'cancel_non_pay_transaction')
def cancel_non_pay_tra():
    '''发送激活邮件'''
    from order.models import Transaction
    unpay_tra_list = Transaction.objects.filter(status=1)
    for i in unpay_tra_list.all():
        if (django.utils.timezone.now() - i.create_time).seconds > 3600:
            i.status = 0
            i.delete()

@app.task(name = 'create_user_commodity_matrix')
def create_matrix():
    import user.models
    import commodity.models
    redis_connect = Redis(host='localhost', port=6379, db=10, decode_responses=True)
    K = 10
    rec_num = 10
    user_list = user.models.User.objects.all()
    mer_list = commodity.models.Merchandise.objects.filter(status=1).all()
    user_favourite_dict = dict()
    mer_favourite_dict = dict()
    if len(mer_list) < 20:
        return
    for user in user_list:
        user_favourite_dict[user.id] = user.favorite_merchandise
    for mer in mer_list:
        mer_favourite_dict[mer.id] = mer.who_favourite
    mer_id_j = dict()
    for j in range(len(mer_list)):
        mer_id_j[mer_list[j].id] = j
    relations_matrix = [[0 for i in range(len(mer_list))] for j in range(len(mer_list))]
    for i in range(len(mer_list)-1):
        for j in range(i+1, len(mer_list)):
            set1 = set(mer_list[i].who_favourite) & set(mer_list[j].who_favourite)
            set2 = set(mer_list[i].who_favourite) | set(mer_list[j].who_favourite)
            relations_matrix[i][j] = len(list(set1))/len(list(set2))**0.5
            relations_matrix[j][i] = relations_matrix[i][j]
    # 计算商品相似度得导矩阵
    mer_mer_favo_list = [list() for i in range(len(mer_list))]
    for i in range(len(mer_list)):
        for j in range(len(mer_list)):
            if j == i:
                continue
            else:
                mer_mer_favo_list[i].append((mer_list[j].id, relations_matrix[i][j]))
    # 获得单个商品和其他商品的相似度关系，元组列表的形式存储
    for i in range(len(mer_mer_favo_list)):
        mer_mer_favo_list[i] = sorted(mer_mer_favo_list[i], key=lambda x: (x[1], x[0]), reverse=True)
    # 进行排序
    user_mer = [[0 for j in range(len(mer_list))] for i in range(len(user_list))]
    #初始化用户和商品喜爱关系的矩阵
    for i in range(len(user_list)):
        current_user = user_list[i]
        current_user_favourite_list = current_user.favorite_merchandise
        current_user_favourite_set = set(current_user_favourite_list)
        if len(current_user_favourite_list) == 0:
            for j in range(len(mer_list)):
                user_mer[i][j] = 0
            continue
        for j in range(len(mer_list)):
            mer_K_list = []
            for k in range(K):
                mer_K_list.append(mer_mer_favo_list[j][k][0])
            current_mer_favo_set = current_user_favourite_set & set(mer_K_list)
            if len(current_mer_favo_set) == 0:
                user_mer[i][j] = 0
                continue
            p_user_mer = 0
            for same_favo_mer in current_mer_favo_set:
                p_user_mer += relations_matrix[mer_id_j[same_favo_mer]][j] * 5
            user_mer[i][j] = p_user_mer
    user_mer_order_list = [list() for i in range(len(user_list))]
    for i in range(len(user_list)):
        current_user = user_list[i]
        current_user_favourite_list = current_user.favorite_merchandise
        for j in range(len(mer_list)):
            if mer_list[j].id not in current_user_favourite_list:
                user_mer_order_list[i].append((mer_list[j].id, user_mer[i][j]))
    for i in range(len(user_mer_order_list)):
        user_mer_order_list[i] = sorted(user_mer_order_list[i], key=lambda x: (x[1], x[0]), reverse=True)
    for i in range(len(user_list)):
        cur_recommend_list = []
        for j in range(min(rec_num, len(user_mer_order_list[i]))):
            cur_recommend_list.append(user_mer_order_list[i][j])
        user_list[i].user_recommend_list = cur_recommend_list
        user_list[i].save()



@app.task(name = 'create_user_commodity_matrix')
def create_recommend_list_by_browsing():
    import commodity.models
    conn = get_redis_connection('default')
    mer_list = commodity.models.Merchandise.objects.filter(status=1).order_by('-browse_number').all()
    id_list = []
    for mer in mer_list:
        id_list.append(mer.id)
    key = "recommend_list"
    conn.set(key, str(id_list[0:30]))
