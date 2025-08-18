import re
from django.core.exceptions import ValidationError


class CardValidationMixin:
    """
        A mixin that provides strong validation for Card model fields.
        Includes validation for:
        - card number (16 digits and Luhn compliant)
        - expiry date (multiple formats supported)
        - phone number (various valid formats)
        - status (active, inactive, expired)
    """

    def clean_card_number(self):
        """
            Validates the card number:
            1. Must be exactly 16 digits (ignoring spaces or non-digit characters)
            2. Must pass the Luhn algorithm check
        """
        card_number = self.cleaned_data.get("card_number", "")
        digits = "".join(ch for ch in card_number if ch.isdigit())

        if not re.fullmatch(r"\d{16}", digits):
            raise ValidationError("The card number must be 16 digits long")

        if not self._luhn_check(digits):
            raise ValidationError("The card number is invalid (does not comply with the Luhn algorithm)")

        return digits

    def clean_expire(self):
        """
            Validates the expiry date of the card.
            Supports multiple formats such as:
            - MM/YY
            - YYYY-MM
            - MM.YYYY
        """
        expire = str(self.cleaned_data.get("expire", "")).strip()

        if not expire:
            raise ValidationError("This field is required")

        patterns = [
            r"^(0[1-9]|1[0-2])/\d{2}$",
            r"^\d{4}-(0[1-9]|1[0-2])$",
            r"^(0[1-9]|1[0-2])\.\d{4}$",
        ]
        if not any(re.fullmatch(p, expire) for p in patterns):
            raise ValidationError("Expire date is wrong  formatted")

        return expire

    def clean_phone(self):
        """
            Validates the phone number.
            Supports multiple formats including:
            - +998XXXXXXXXX
            - 99 973 03 03
            - 973-03-03
            - 991234567
            If empty, returns an empty string.
        """
        phone = str(self.cleaned_data.get("phone", "")).strip()

        if not phone:
            return ""

        patterns = [
            r"^\+998\d{9}$",
            r"^\d{2}\s\d{3}\s\d{2}\s\d{2}$",
            r"^\d{3}-\d{2}-\d{2}$",
            r"^\d{9}$",
        ]
        if not any(re.fullmatch(p, phone) for p in patterns):
            raise ValidationError("Phone number is wrong formatted")

        return phone

    def clean_status(self):
        """
           Validates the card status.
           Only 'active', 'inactive', or 'expired' are allowed values.
        """
        status = self.cleaned_data.get("status", "").lower()
        valid_statuses = {"active", "inactive", "expired"}
        if status not in valid_statuses:
            raise ValidationError("Status be only active/inactive/expired ")
        return status

    def _luhn_check(self, number: str) -> bool:
        """
            Checks the card number using the Luhn algorithm.
            Returns True if valid, False otherwise.
        """
        total = 0
        reverse_digits = number[::-1]
        for i, d in enumerate(reverse_digits):
            n = int(d)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0
