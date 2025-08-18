from django.contrib import admin
from apps.cards.models.card import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("format_card_number", "format_expire", "format_phone", "status", "balance")
    list_filter = ('card_number', 'expire', 'phone', 'status')
    search_fields = ("card_number", "phone")
