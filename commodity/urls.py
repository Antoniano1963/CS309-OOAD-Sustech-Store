from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views

urlpatterns = [
    # url('user_mobile_homepage/', views.user_mobile_homepage),
    url('commodity_detail/', views.commodity_detail),
    # url('commodity_comments/', views.commodity_comments),
    url('download/', views.download_handler),
    url('add_favorite_merchandise_handler/', views.add_favorite_merchandise_handler),
    # url('add_shopping_trolley/', views.add_shopping_trolley_handler),
    url('add_favorite_business_handler/', views.add_favorite_business_handler),
    url('search_by_class_label_all/', views.search_by_class_label_all),
    # url('add_favorite_business_handler/', views.add_favorite_business_handler),

]
