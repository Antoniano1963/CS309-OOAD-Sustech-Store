from django.contrib import admin
from .models import Task
# from .models import Comment
# from .models import SubComment
from .models import *
# from .models import MerchandiseLabel
# Register your models here.

admin.site.register(Task)