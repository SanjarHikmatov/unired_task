from django.core.management.base import BaseCommand
from apps.cards.models import Card


class Command(BaseCommand):
    """
        Management command to simulate sending messages to filtered cards.

        Usage:
            python manage.py send_fake_message --status=active

        Features:
        - Filters Card objects by given status (default: "active").
        - For each card, generates a fake notification message containing card number and balance.
        - Prints simulated "sending logs" to the console (does not send real messages).
        - Useful for testing and debugging message delivery without integrating Telegram API.
    """

    help = "Send fake messages to filtered cards (simulate Telegram bot messages)."
    help = "Send fake messages to filtered cards (simulate Telegram bot messages)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            type=str,
            default="active",
            help="Filter cards by status (default: active)",
        )

    def handle(self, *args, **options):
        status = options["status"]

        cards = Card.objects.filter(status=status)

        if not cards.exists():
            self.stdout.write(self.style.WARNING(f"No cards found with status='{status}'"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {cards.count()} cards with status='{status}'"))
        self.stdout.write(self.style.SUCCESS("Simulating message sending..."))

        for card in cards:
            message = f" Your card number ({card.card_number}) is active and it has {card.balance} UZS!"

            self.stdout.write(f"[FAKE SEND] To: {card.phone or 'N/A'} | Message: {message}")

        self.stdout.write(self.style.SUCCESS("All messages simulated successfully!"))
