from django.contrib import admin
from apps.transfers.models.transfer_models import Transfer
# Register your models here.
@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('id',"ext_id")