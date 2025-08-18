from django.db import models
from django.utils.translation import gettext_lazy as _


class Card(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")
        EXPIRED = "expired", _("Expired")

    card_number = models.CharField(
        max_length=16,
        unique=True,
        verbose_name=_("Card Number")
    )
    expire = models.CharField(
        max_length=10,
        verbose_name=_("Expiry Date")
    )
    phone = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name=_("Phone Number")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Card Status")
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_("Account Balance")
    )

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")



    def __str__(self):
        return f"{self.format_card_number} ({self.status})"

    @property
    def format_card_number(self):
        """Format card number: 8600123456789012 -> 8600 1234 5678 9012"""
        return " ".join([self.card_number[i:i+4] for i in range(0, len(self.card_number), 4)])

    @property
    def format_phone(self):
        """Format phone: 998991234567 -> +998 99 123 45 67"""
        if not self.phone or self.phone in ("(empty)", ""):
            return "-"
        digits = "".join(filter(str.isdigit, self.phone))

        if digits.startswith("998") and len(digits) == 12:
            return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"

        if len(digits) == 9:
            return f"+998 {digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}"
        return self.phone

    @property
    def format_expire(self):
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
        if not self.expire:
            return "-"

        digits = "".join(ch for ch in self.expire if ch.isdigit())

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

        return self.expire

