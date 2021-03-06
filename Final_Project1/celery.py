# bookstore/celery.py
import datetime
import os
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone
from django_redis import get_redis_connection
from redis import Redis
from celery import Celery
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .settings import EMAIL_FROM
from django.db import transaction
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



app.conf.beat_schedule = {
    'cancel_over_ddl_task-every-60-seconds': {
        'task': 'cancel_over_ddl_task',
        'schedule': 60.0,
        'args': ()
    },
    'cancel_non_pay_tra-every-60-seconds': {
        'task': 'cancel_non_pay_tra',
        'schedule': 60.0,
        'args': ()
    },
    'create_user_commodity_matrix-every-86400-seconds': {
        'task': 'create_user_commodity_matrix',
        'schedule': 86400.0,
        'args': ()
    },
    'create_recommend_list_by_browsing-every-3600-seconds': {
        'task': 'create_recommend_list_by_browsing',
        'schedule': 3600.0,
        'args': ()
    },
}
app.conf.timezone = 'UTC'

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(60.0, cancel_non_pay_tra.s(), name='cancel non-pay transactions every 60 seconds')
#     sender.add_periodic_task(60.0, create_user_commodity_matrix.s(), name='create recommend matrix every 60 seconds')
#     sender.add_periodic_task(60.0, cancel_over_ddl_task.s(), name='cancel over ddl tasks every 60 seconds')
#     sender.add_periodic_task(60.0, create_recommend_list_by_browsing.s(), name='create recommend list by browsing number every 60 second')



register = ''
change_pwd = ''
logo = None
logo_inv = None
# with open('Email_template/', 'r') as f:
#     register = f.read()
with open('Final_Project1/Email_template/ChangePassword.html', 'r') as f:
    change_pwd = f.read()
with open('Final_Project1/Email_template/register.html', 'r') as f:
    register = f.read()
with open('Final_Project1/Email_template/notice_mer2.html', 'r') as f:
    notice_mer = f.read()
with open('Final_Project1/Email_template/notice_withoutmer.html', 'r') as f:
    notice_without = f.read()
# with open('utils/email_templates/logoPure.4b5e7613.png', 'rb') as f:
#     logo = MIMEImage(f.read())
#     logo.add_header('Content-ID', '<image1>')
# with open('utils/email_templates/logoPureInv.png', 'rb') as f:
#     logo_inv = MIMEImage(f.read())
#     logo_inv.add_header('Content-ID', '<image2>')


@app.task(name = 'send_email', time_limit=15)
def send_active_email(code, email, current_user_name, img_url, price, mer_name='', rela_mer=None, type=2):
    '''??????????????????'''
    import commodity.models
    import user.models
    subject = '??????Sustech Store ?????????' # ??????
    message = ''
    sender = EMAIL_FROM # ?????????
    receiver = [email] # ???????????????
    # html_message1 = '<div>Code is {}</div>'.format(code)
    html_message2 = '<div>??????????????? is {}</div>'.format(code)
    # html_message3 = '<div>????????????????????? Code is {}</div>'.format(code)
    print(email)
    # html_message = html_message1 if type ==1 else html_message2
    if type == 1:
        subject = '?????????????????? Sustech Store ???????????????????????????????????????Sustech Store'
        html_message = register.format(username=current_user_name, code=code)
    elif type == 2:
        subject = '?????????????????? Sustech Store ??????????????????????????????Sustech Store'
        if rela_mer:
            html_message = notice_mer.format(username=current_user_name, info=code, mer_name=mer_name, mer_photo_url=img_url, price=price)
        else:
            html_message = notice_without.format(username=current_user_name, info=code)
    else:
        subject = '?????????????????? Sustech Store ????????????????????????????????????Sustech Store'
        html_message = change_pwd.format(username=current_user_name, code=code)
        # html_message = html_message3
    print(code)
    # print(html_message)
    print(receiver)

    send_mail(subject, message, sender, receiver, html_message=html_message)


@transaction.atomic
@app.task(name = 'cancel_non_pay_tra')
def cancel_non_pay_tra():
    '''??????????????????'''
    from order.models import Transaction
    unpay_tra_list = Transaction.objects.filter(status=1)
    for i in unpay_tra_list.all():
        if (django.utils.timezone.now() - i.create_time).seconds > 3600:
            sid = transaction.savepoint()
            try:
                i.status = 0
                current_mer = i.transaction_merchandise
                current_mer.status = 1
                current_mer.save()
                i.delete()
            except:
                transaction.savepoint_rollback(sid)
            transaction.savepoint_commit(sid)


@transaction.atomic
@app.task(name = 'cancel_over_ddl_task')
def cancel_over_ddl_task():
    from chat.utils import send_notice
    '''??????????????????'''
    from task.models import Task
    notasker_list = Task.objects.filter(task_status=7)
    for i in notasker_list.all():
        if django.utils.timezone.now() > i.ddl_time:
            sid = transaction.savepoint()
            try:
                current_uploader = i.upload_user
                current_uploader.money += i.price
                current_uploader.save()
                if i.task_type == 1:
                    current_tra = i.relation_transaction
                    current_tra.has_task = False
                    current_tra.save()
                send_notice(i.upload_user.id,
                            '??????{}??????DDL??????{}????????????'.format(i.name, i.ddl_time.strftime("%Y-%m-%d")))
                i.delete()
            except:
                transaction.savepoint_rollback(sid)
            transaction.savepoint_commit(sid)


@app.task(name = 'create_user_commodity_matrix')
def create_user_commodity_matrix():
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
    # ?????????????????????????????????
    mer_mer_favo_list = [list() for i in range(len(mer_list))]
    for i in range(len(mer_list)):
        for j in range(len(mer_list)):
            if j == i:
                continue
            else:
                mer_mer_favo_list[i].append((mer_list[j].id, relations_matrix[i][j]))
    # ?????????????????????????????????????????????????????????????????????????????????
    for i in range(len(mer_mer_favo_list)):
        mer_mer_favo_list[i] = sorted(mer_mer_favo_list[i], key=lambda x: (x[1], x[0]), reverse=True)
    # ????????????
    user_mer = [[0 for j in range(len(mer_list))] for i in range(len(user_list))]
    #?????????????????????????????????????????????
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



@app.task(name = 'create_recommend_list_by_browsing')
def create_recommend_list_by_browsing():
    import commodity.models
    conn = get_redis_connection('default')
    mer_list = commodity.models.Merchandise.objects.filter(status=1).order_by('-browse_number').all()
    id_list = []
    for mer in mer_list:
        id_list.append(mer.id)
    key = "recommend_list"
    conn.set(key, str(id_list[0:30]))


@app.task(name = 'add_credit_score')
def add_credit_score():
    import user.models
    user_List = user.models.User.objects.all()
    for user in user_List:
        user.credit_points += 1
        if user.credit_points >= 10:
            user.credit_points = 10
        
