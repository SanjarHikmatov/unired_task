import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
user_chat_id = os.getenv('chat_id')

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
    chat_id = user_chat_id
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



def mask_card_number(card_number):
    """Format card number: 8600123456789012 -> 8600 1234 5678 9012"""
    return " ".join([card_number[i:i+4] for i in range(0, len(card_number), 4)])

def mask_phone(phone):
    """Format phone: 998991234567 -> +998 99 123 45 67"""
    if not phone or phone in ("(empty)", ""):
        return "-"
    digits = "".join(filter(str.isdigit, phone))

    if digits.startswith("998") and len(digits) == 12:
        return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"

    if len(digits) == 9:
        return f"+998 {digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}"
    return phone

def mask_expire(expire):
    """
    Normalize and show expiry date as MM/YY (e.g. 12/24),
    even if stored in formats like:
    - 12/2024
    - 2024-12
    - 12.2024
    - 12-2024
    - 2024  (year only)
    - 12    (month only)
    """
    if not expire:
        return "-"

    digits = "".join(ch for ch in expire if ch.isdigit())

    if len(digits) == 6 and digits.startswith("20"):
        year = digits[:4]
        month = digits[4:]
        return f"{month}/{year[-2:]}"

    if len(digits) == 6:
        month = digits[:2]
        year = digits[2:]
        return f"{month}/{year[-2:]}"

    if len(digits) == 4:
        month = digits[:2]
        year = digits[2:]
        return f"{month}/{year}"

    if len(digits) == 4 and digits.startswith("20"):
        year = digits[-2:]
        return f"01/{year}"

    if len(digits) <= 2:
        month = digits.zfill(2)
        return f"{month}/--"

    return expire

