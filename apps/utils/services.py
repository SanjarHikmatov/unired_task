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
    643: Decimal("1.00"),  # RUB
    840: Decimal("1.00"),  # USD
}

logger = logging.getLogger(__name__)


def generate_otp(length: int = 6) -> str:
    """
        Generate a random numeric OTP code with a default length of 6 digits.
        Example: '582934'
    """
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def send_telegram_message(message: str) -> bool:
    """
        Send a message to a Telegram chat using the Bot API.

        Requires:
        - TELEGRAM_BOT_TOKEN (from .env)
        - chat_id (from .env)
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
    """
        Convert an amount to the target currency using static exchange rates.

        :param amount: Decimal amount to convert
        :param currency: Currency code (e.g., 643=RUB, 840=USD)
        :return: Converted amount rounded to 2 decimals
    """
    rate = STATIC_RATES.get(currency)
    if rate is None:
        raise ValueError("Currency not supported")
    return (amount * rate).quantize(Decimal("0.01"))


def mask_card_number(card_number: str) -> str:
    """
    Format a card number by grouping digits in blocks of 4.
    Example: 8600123456789012 -> '8600 1234 5678 9012'
    """
    return " ".join([card_number[i:i + 4] for i in range(0, len(card_number), 4)])


def mask_phone(phone: str) -> str:
    """
        Format a phone number into a standard readable form.

        Examples:
        - 998991234567 -> '+998 99 123 45 67'
        - 991234567 -> '+998 99 123 45 67'
        - Empty/invalid -> '-'
    """
    if not phone or phone in ("(empty)", ""):
        return "-"
    digits = "".join(filter(str.isdigit, phone))

    if digits.startswith("998") and len(digits) == 12:
        return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"

    if len(digits) == 9:
        return f"+998 {digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}"
    return phone


def mask_expire(expire: str) -> str:
    """
        Normalize and display a card expiry date in MM/YY format.

        Supported input formats:
        - 12/2024 -> '12/24'
        - 2024-12 -> '12/24'
        - 12.2024 -> '12/24'
        - 12-2024 -> '12/24'
        - 2024    -> '01/24' (assumes January if only year is provided)
        - 12      -> '12/--' (month only, year unknown)

        If empty, returns '-'.
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

    if len(digits) == 4 and not digits.startswith("20"):
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
