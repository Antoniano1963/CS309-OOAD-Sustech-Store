from django.contrib import admin
from .models import Merchandise
# from .models import Comment
# from .models import SubComment
from .models import *
# from .models import MerchandiseLabel
# Register your models here.

admin.site.register(Merchandise)
# admin.site.register(Comment)
# admin.site.register(SubComment)
admin.site.register(ClassLevel2)
admin.site.register(ClassLevel1)