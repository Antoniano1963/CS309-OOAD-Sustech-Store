from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views

urlpatterns = [
    # url('user_mobile_homepage/', views.user_mobile_homepage),
    url('pc_login/', views.login_fuc),
    url('register/', views.register),
    url('logout/', views.logout),
    url('mobile_login/', views.mobile_login),
    url('upload_commodity/', views.upload_commodity),
    url('wait_payment/', views.wait_payment_fuc),
    # url('register_email/', views.register_email),
    url('new_register_email/', views.new_register_email),
    # url('shopping_trolley_fuc/', views.shopping_trolley_fuc),
    # url('user_search/', views.user_search),
    url('on_sailing/', views.all_user_selling_merchandise),
    url('wait_deliver/', views.wait_deliver_fuc),
    url('wait_receiving_fuc/', views.wait_receiving_fuc),
    url('wait_comment_fuc/', views.wait_comment_fuc),
    url('success_fuc/', views.success_fuc),
    url('wait_payment_fuc/', views.wait_payment_fuc),
    url('all_user_favorite_merchandise/', views.all_user_favorite_merchandise),
    url('all_user_favorite_business/', views.all_user_favorite_business),
    url('activate/', views.activate),
    url('get_address_list/', views.get_address_list),
    # url('change_default_addr/', views.change_default_addr),
    url('upload_head_photo/', views.upload_head_photo),
    url('get_user_details/', views.get_user_details),
    url('upload_QR_Code/', views.upload_QR_Code),
    url('modify_self_info/', views.modify_self_info),
    url('add_address/', views.add_address),
    url('recharge/', views.recharge),
    url('upload_head_photo/', views.upload_head_photo),
    url('upload_QR_code/', views.upload_QR_Code),
    url('add_cart/', views.add_cart),
    url('cart_show/', views.cart_show),
    url('cart_del/', views.cart_del),
    url('get_recommend_list/', views.get_recommend_list),
    url('upload_QR_code/', views.upload_QR_Code),
    url('change_password/', views.change_password),
    url('change_pay_password/', views.change_pay_password),
    url('get_all_comments/', views.get_all_comments),
    url('user_page/', views.user_page),
    url('wait_payment_fuc_seller/', views.wait_payment_fuc_seller),
    url('wait_deliver_fuc_seller/', views.wait_deliver_fuc_seller),
    url('wait_receiving_fuc_seller/', views.wait_receiving_fuc_seller),
    url('wait_comment_fuc_seller/', views.wait_comment_fuc_seller),
    url('success_fuc_seller/', views.success_fuc_seller),
    url('get_problem_list/', views.get_problem_list),
    url('delete_address/', views.delete_address),
    url('delete_commodity/', views.delete_commodity),
    url('get_notification_list/', views.get_notification_list),
    url('get_QR_Code/', views.get_QR_Code),
    url('forget_password/', views.forget_password),
    url('forget_pay_password/', views.forget_pay_password),
    url('forget_pay_password_email/', views.forget_pay_password_email),
    url('forget_password_email/', views.forget_password_email),

]
