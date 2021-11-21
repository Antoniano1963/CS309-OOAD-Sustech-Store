"""Final_Project1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from commodity.views import MysearchView
from Final_Project1 import settings
from django.conf.urls.static import serve
urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    url('api/login0/', include('user.urls')),
    url('api/commodity/', include('commodity.urls')),
    url('api/transaction/', include('order.urls')),
    url('api/chat/', include('chat.urls')),
    url('api/search/', MysearchView()),
    url('api/dialogue/', include('dialogue.urls')),
    url('api/task/', include('task.urls')),
    url('api/supermanager/', include('supermanager.urls')),
]