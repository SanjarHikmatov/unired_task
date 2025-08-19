import os
import requests
from dotenv import load_dotenv
from celery import shared_task
from apps.cards.models.card import Card
from apps.transfers.models.transfer_models import Transfer

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("chat_id")


@shared_task
def telegram_report():
    """
    Celery task that generates a summary report of the system
    and sends it to a specified Telegram chat using a bot.

    The report includes:
    - Total number of cards in the system
    - Total number of transfers in the system
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    total_card_count = Card.objects.count()
    total_transfer_count = Transfer.objects.count()

    text = (
        f"This is the total system report:\n"
        f" - Total Cards: {total_card_count}\n"
        f" - Total Transfers: {total_transfer_count}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return f"Report successfully sent: {response.text}"
    except requests.RequestException as e:
        return f"Failed to send report: {e}, response={getattr(e, 'response', None)}"
