from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.core.files.storage import default_storage
from .models import Card
from .forms.create import CardForm
from .tasks import import_cards_from_excel_task
from apps.cards.filters.card_filter import BalanceFilter, PhoneFilter, ExpireYearFilter

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("format_card_number", "expire", "phone", "status", "balance")
    list_filter = ("status", PhoneFilter,ExpireYearFilter, BalanceFilter)
    search_fields = ("card_number", "phone")
    form = CardForm
    change_list_template = "admin/cards/card_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-excel/", self.import_excel, name="cards_card_import_excel"),
        ]
        return custom_urls + urls

    def import_excel(self, request):
        """
            Admin panel orqali Excel fayl yuklash va uni
            Celery task yordamida asinxron tarzda import qilishni boshqaradi.
        """
        if request.method == "POST" and request.FILES.get("excel_file"):
            excel_file = request.FILES["excel_file"]

            file_path = default_storage.save(f"tmp/{excel_file.name}", excel_file)

            result = import_cards_from_excel_task.delay(default_storage.path(file_path))

            self.message_user(
                request,
                f"Excel import job has been started (task id: {result.id})",
                level=messages.INFO,
            )
            return redirect(reverse("admin:cards_card_changelist"))

        return render(request, "admin/cards/import_excel.html")
