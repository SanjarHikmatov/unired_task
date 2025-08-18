import random
import zipfile


def luhn_generate(prefix: str, length: int = 16) -> str:
    """
        Generates a valid card number using the Luhn algorithm.
        prefix: starting digits of the card (e.g., '8600')
        length: total length of the card number (default 16)
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


def generate_cards_excel(filename="cards.xlsx", rows=500):
    """
        Generates an Excel (.xlsx) file with random card data.
        All card numbers are generated to be valid according to the Luhn algorithm.

        Args:
            filename (str): Output file name (default "cards.xlsx")
            rows (int): Number of rows/cards to generate (default 500)
    """
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
        <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
        <Default Extension="xml" ContentType="application/csv"/>
        <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
        <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.opencsvformats-officedocument.spreadsheetml.worksheet+xml"/>
    </Types>
    """

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
    </Relationships>
    """

    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
              xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <sheets>
        <sheet name="Cards" sheetId="1" r:id="rId1"/>
      </sheets>
    </workbook>
    """

    workbook_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
    </Relationships>
    """

    columns = ["card_number", "expire", "phone", "status", "balance"]
    statuses = ["active", "inactive", "expired"]
    expire_formats = ["{:02d}/20{:02d}", "20{:02d}-{:02d}", "{:02d}.20{:02d}", "{:02d}-20{:02d}"]
    phone_formats = ["99 973 {:02d} {:02d}", "973-{:02d}-{:02d}", "+99899{:02d}{:02d}{:02d}", "(empty)"]
    card_prefixes = ["8600", "5614", "4916"]

    rows_xml = "<row>" + "".join(f"<c t='inlineStr'><is><t>{col}</t></is></c>" for col in columns) + "</row>"

    for _ in range(rows):
        prefix = random.choice(card_prefixes)
        card_number = luhn_generate(prefix, 16)

        year = random.randint(2024, 2028)
        month = random.randint(1, 12)
        fmt = random.choice(expire_formats)
        expire = fmt.format(month, year % 100) if "{}" in fmt else fmt.format(month, year % 100)

        fmt_phone = random.choice(phone_formats)
        if "(empty)" in fmt_phone or fmt_phone == "":
            phone = fmt_phone
        elif fmt_phone.count("{") == 2:
            phone = fmt_phone.format(random.randint(10, 99), random.randint(10, 99))
        elif fmt_phone.count("{") == 3:
            phone = fmt_phone.format(random.randint(10, 99), random.randint(10, 99), random.randint(10, 99))
        else:
            phone = fmt_phone

        status = random.choice(statuses)
        balance = round(random.uniform(0, 1_200_000_000), 2)

        row = [card_number, expire, phone, status, balance]
        rows_xml += "<row>" + "".join(f"<c t='inlineStr'><is><t>{v}</t></is></c>" for v in row) + "</row>"

    sheet = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <sheetData>
        {rows_xml}
      </sheetData>
    </worksheet>
    """

    with zipfile.ZipFile(filename, "w") as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        z.writestr("xl/worksheets/sheet1.xml", sheet)

    print(f"{rows} valid cards (Luhn) generated in: {filename}")


generate_cards_excel("cards.xlsx", rows=500)
