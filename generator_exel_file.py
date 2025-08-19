# cards/utils.py
import random
from openpyxl import Workbook


def luhn_generate(prefix: str, length: int = 16) -> str:
    """
        Generate a valid card number using the Luhn algorithm.

        :param prefix: Card number prefix (e.g., "8600")
        :param length: Total length of the card number (default: 16)
        :return: Valid card number as a string
    """
    number = [int(x) for x in prefix]

    while len(number) < length - 1:
        number.append(random.randint(0, 9))

    total = 0
    reverse_digits = number[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d

    check_digit = (10 - (total % 10)) % 10
    number.append(check_digit)

    return "".join(map(str, number))


def generate_cards_excel(filename: str = "cards.xlsx", rows: int = 500):
    """
        Generate a random Excel file with fake card data.

        :param filename: Output Excel file name (default: 'cards.xlsx')
        :param rows: Number of card records to generate (default: 500)
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Cards"

    columns = ["card_number", "expire", "phone", "status", "balance"]
    ws.append(columns)

    statuses = ["active", "inactive", "expired"]
    expire_formats = ["{:02d}/{:02d}", "{:02d}-{:02d}", "{:02d}.{:02d}"]
    phone_formats = [
        "99 973 {:02d} {:02d}",
        "973-{:02d}-{:02d}",
        "+99899{:02d}{:02d}{:02d}",
        ""
    ]
    card_prefixes = ["8600", "5614", "4916"]

    for _ in range(rows):
        prefix = random.choice(card_prefixes)
        card_number = luhn_generate(prefix, 16)

        month = random.randint(1, 12)
        year = random.randint(24, 28)  # Year in short format (e.g., 24 = 2024)
        expire = random.choice(expire_formats).format(month, year)

        fmt_phone = random.choice(phone_formats)
        if fmt_phone == "":
            phone = ""
        elif fmt_phone.count("{") == 2:
            phone = fmt_phone.format(random.randint(10, 99), random.randint(10, 99))
        elif fmt_phone.count("{") == 3:
            phone = fmt_phone.format(random.randint(10, 99), random.randint(10, 99), random.randint(10, 99))
        else:
            phone = fmt_phone

        status = random.choice(statuses)
        balance = round(random.uniform(0, 1_200_000_000), 2)

        ws.append([card_number, expire, phone, status, balance])

    wb.save(filename)
    print(f"{rows} cards generated in {filename}")


generate_cards_excel("cards.xlsx", 500)
