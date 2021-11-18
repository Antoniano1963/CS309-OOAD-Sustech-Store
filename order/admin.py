from django.contrib import admin
from .models import Transaction, TransactionProblem
# Register your models here.
admin.site.register(Transaction)
admin.site.register(TransactionProblem)