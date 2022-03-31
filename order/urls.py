from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views

urlpatterns = [
    # url('user_mobile_homepage/', views.user_mobile_homepage),
    url('detail/', views.detail_fuc),
    url('post_transaction/', views.post_transaction),
    url('commit_transaction_total/', views.commit_transaction_total),
    url('get_identify_code/', views.get_identify_code),
    url('commit_transaction_virtual/', views.commit_transaction_virtual),
    url('commit_transaction_face/', views.commit_transaction_face),
    url('already_send_transaction/', views.already_send_transaction),
    url('already_receive_transaction/', views.already_receive_transaction),
    url('comment_transaction/', views.comment_transaction),
    url('transaction_has_problem/', views.transaction_has_problem),
    url('cancel_transaction/', views.cancel_transaction),
    # url('commit_transaction_QR_code_start/', views.commit_transaction_QR_code_start),
    # url('commit_transaction_QR_code_ready/', views.commit_transaction_QR_code_ready),
    url('commit_transaction_QR_code_commit/', views.commit_transaction_QR_code_commit),
    # url('commit_transaction_QR_code_commit_receive/', views.commit_transaction_QR_code_commit_receive),
    url('commit_transaction_face/', views.commit_transaction_face),
    url('get_tra_rela_problem/', views.get_tra_rela_problem),
]
