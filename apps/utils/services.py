import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

import requests
import logging
import random
from decimal import Decimal

ALLOWED_CURRENCIES = {643, 840}
STATIC_RATES = {
    643: Decimal("1.00"),
    840: Decimal("1.00"),
}


logger = logging.getLogger(__name__)
def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def send_telegram_message(message: str) -> bool:
    """
    Haqiqiy Telegram bot orqali xabar yuboradi.
    Chat ID va token avvaldan berilgan.
    """
    token = TELEGRAM_BOT_TOKEN
    chat_id = 1488868298
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    try:

        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"[TELEGRAM] Message sent: {message}")
        return True
    except requests.RequestException as e:
        logger.error(f"[TELEGRAM] Failed to send message: {e}")
        return False

def calculate_exchange(amount: Decimal, currency: int) -> Decimal:
    rate = STATIC_RATES.get(currency)
    if rate is None:
        raise ValueError("Currency not supported")
    return (amount * rate).quantize(Decimal("0.01"))


asd = send_telegram_message('salom')