from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.utils.models.base_model import BaseModel


class Card(BaseModel):
    """
        Represents a bank/payment card entity with attributes like
        card number, expiry date, phone number, status, and balance.
    """

    class Status(models.TextChoices):
        """
            Enumeration for card statuses.
            Used as choices for the `status` field.
        """
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")
        EXPIRED = "expired", _("Expired")

    card_number = models.CharField(
        max_length=16,
        unique=True,
        verbose_name=_("Card Number"),
        help_text=_("The 16-digit unique card number (e.g. 8600123412341234).")
    )
    expire = models.CharField(
        max_length=10,
        verbose_name=_("Expiry Date"),
        help_text=_("Card expiry date in flexible formats (e.g. 12/24, 12/2024, 2024-12).")
    )
    phone = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name=_("Phone Number"),
        help_text=_("Optional phone number linked to the card.")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Card Status"),
        help_text=_("Indicates whether the card is active, inactive, or expired.")
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_("Account Balance"),
        help_text=_("Current balance of the card account.")
    )

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    def __str__(self) -> str:
        """
            String representation of the card object.

            Returns:
                str: A formatted string showing the card number and status.
            Example:
                "8600 1234 5678 9012 (active)"
        """
        return f"{self.format_card_number} ({self.status})"



    @property
    def format_card_number(self) -> str:
        """
            Format the raw card number into groups of 4 digits for readability.

            Example:
                8600123456789012 -> "8600 1234 5678 9012"
        """
        return " ".join([self.card_number[i:i+4] for i in range(0, len(self.card_number), 4)])

    @property
    def format_phone(self) -> str:
        """
            Format the phone number into a readable format.

            Examples:
                - 998991234567 -> "+998 99 123 45 67"
                - 991234567    -> "+998 99 123 45 67"
                - None or empty -> "-"
        """
        if not self.phone or self.phone in ("(empty)", ""):
            return "-"
        digits = "".join(filter(str.isdigit, self.phone))

        if digits.startswith("998") and len(digits) == 12:
            return f"+998 {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"

        if len(digits) == 9:
            return f"+998 {digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}"
        return self.phone

    @property
    def format_expire(self) -> str:
        """
            Normalize and return expiry date in format `MM/YY`.

            Handles multiple possible input formats:
                - "12/2024"   -> "12/24"
                - "2024-12"   -> "12/24"
                - "12.2024"   -> "12/24"
                - "12-2024"   -> "12/24"
                - "2024"      -> "01/24"
                - "12"        -> "12/--"

            Returns:
                str: Normalized expiry date or "-" if missing.
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
            if digits.startswith("20"):
                year = digits[-2:]
                return f"01/{year}"
            month = digits[:2]
            year = digits[2:]
            return f"{month}/{year}"

        if len(digits) <= 2:
            month = digits.zfill(2)
            return f"{month}/--"

        return self.expire
