from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views

urlpatterns = [
    # url('user_mobile_homepage/', views.user_mobile_homepage),
    url('release_task_transaction/', views.release_task_transaction),
    url('release_task_others/', views.release_task_others),
    url('cancel_task/', views.cancel_task),
    url('get_task/', views.get_task),
    url('task_get_object/', views.task_get_object),
    url('task_send_object/', views.task_send_object),
    url('task_receive_object/', views.task_receive_object),
    url('task_comment/', views.task_comment),
    url('get_task_list/', views.get_task_list),
    url('task_wait_sender_list_up/', views.task_wait_sender_list_up),
    url('task_wait_receive_object_list_up/', views.task_wait_receive_object_list_up),
    url('task_wait_send_to_place_list_up/', views.task_wait_send_to_place_list_up),
    url('task_wait_confirm_receive_list_up/', views.task_wait_confirm_receive_list_up),
    url('task_wait_confirm_comment_list_up/', views.task_wait_confirm_comment_list_up),
    url('task_wait_confirm_success_list_up/', views.task_wait_confirm_success_list_up),
    url('task_wait_receive_object_list_sender/', views.task_wait_receive_object_list_sender),
    url('task_wait_send_to_place_list_sender/', views.task_wait_send_to_place_list_sender),
    url('task_wait_confirm_receive_list_sender/', views.task_wait_confirm_receive_list_sender),
    url('task_wait_comment_list_sender/', views.task_wait_comment_list_sender),
    url('task_wait_confirm_success_list_sender/', views.task_wait_confirm_success_list_sender),
    url('task_all_relative_list_receive/', views.task_all_relative_list_receive),
    url('get_recommend_tasks/', views.get_recommend_tasks),
    url('get_all_task_list_up/', views.get_all_task_list_up),
    url('get_all_task_list_tasker/', views.get_all_task_list_tasker),
    url('transaction_relation_task/', views.transaction_relation_task),
]
