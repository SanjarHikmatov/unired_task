from django.contrib import admin
from apps.transfers.models.transfer_models import Transfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('id',"ext_id")