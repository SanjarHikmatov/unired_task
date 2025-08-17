import random
import zipfile

def generate_cards_excel(filename="cards.xlsx", rows=500):
    """
    This function creates an Excel (.xlsx) file without using any external packages.
    The file will contain random card data such as card number, expiration date,
    phone number, status, and balance.
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
        card_number = prefix + "".join(str(random.randint(0, 9)) for _ in range(12))

        year = random.randint(2024, 2028)
        month = random.randint(1, 12)
        fmt = random.choice(expire_formats)
        if "{}" in fmt:
            expire = fmt.format(year, month)
        else:
            expire = fmt.format(month, year % 100)

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

    print(f"✅ {rows} cards generated in: {filename}")


generate_cards_excel("cards.xlsx", rows=500)
