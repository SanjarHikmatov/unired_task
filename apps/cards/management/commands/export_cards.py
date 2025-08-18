import csv
from django.core.management.base import BaseCommand
from apps.cards.models import Card


class Command(BaseCommand):
    """
        Management command: Exports cards to a CSV file.
        Optional filters (--status, --card_number, --phone) can be used
        to export only the required records.
    """

    help = "Export cards to CSV with optional filters"

    def add_arguments(self, parser):
        parser.add_argument("--status", type=str, help="Filter by status (active, inactive, expired)")
        parser.add_argument("--card_number", type=str, help="Filter by card number")
        parser.add_argument("--phone", type=str, help="Filter by phone")

    def handle(self, *args, **options):
        queryset = Card.objects.all()

        if options["status"]:
            queryset = queryset.filter(status=options["status"].lower())

        if options["card_number"]:
            queryset = queryset.filter(card_number__icontains=options["card_number"].replace(" ", ""))

        if options["phone"]:
            queryset = queryset.filter(phone__icontains=options["phone"].replace(" ", ""))

        with open("cards_export.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["card_number", "expire", "phone", "status", "balance"])
            for card in queryset:
                writer.writerow([
                    card.format_card_number,   # property dan foydalanamiz
                    card.format_expire,        # normalize qilingan expiry date
                    card.format_phone,         # formatlangan telefon
                    card.status,
                    card.balance,
                ])

        self.stdout.write(self.style.SUCCESS("Cards exported to cards_export.csv"))
