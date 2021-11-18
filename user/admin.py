from django.contrib import admin

# Register your models here.
# login/admin.py

from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.Address)
admin.site.register(models.Comment)
admin.site.register(models.CommentTask)
