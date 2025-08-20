import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.transfers.models import Transfer
from apps.cards.models.card import Card


ALLOWED_CURRENCIES = [643, 840]  # 643 = RUB, 840 = USD
MAX_OTP_ATTEMPTS = 3


class CardValidationMixin:
    """
    A reusable mixin that provides strict validation for Card model fields.
    Includes validation for:
    - Card number (16 digits and Luhn algorithm check)
    - Expiry date (supports multiple formats)
    - Phone number (different acceptable formats)
    - Status (must be active, inactive, or expired)
    """

    def clean_card_number(self):
        """
        Validates the card number:
        1. Must be exactly 16 digits (ignores spaces and non-digit characters)
        2. Must pass the Luhn algorithm check
        """
        card_number = self.cleaned_data.get("card_number", "")
        digits = "".join(ch for ch in card_number if ch.isdigit())

        if not re.fullmatch(r"\d{16}", digits):
            raise ValidationError("The card number must contain exactly 16 digits")

        if not CardValidationMixin._luhn_check(digits):
            raise ValidationError("Invalid card number (failed Luhn check)")

        return digits

    def clean_expire(self):
        """
        Validates the expiry date.
        Supported formats:
        - MM/YY
        - YYYY-MM
        - MM.YYYY
        """
        expire = str(self.cleaned_data.get("expire", "")).strip()

        if not expire:
            raise ValidationError("Expiry date is required")

        patterns = [
            r"^(0[1-9]|1[0-2])/\d{2}$",   # MM/YY
            r"^\d{4}-(0[1-9]|1[0-2])$",   # YYYY-MM
            r"^(0[1-9]|1[0-2])\.\d{4}$",  # MM.YYYY
        ]
        if not any(re.fullmatch(p, expire) for p in patterns):
            raise ValidationError("Invalid expiry date format")

        return expire

    def clean_phone(self):
        """
        Validates the phone number.
        Supported formats:
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
            raise ValidationError("Invalid phone number format")

        return phone

    def clean_status(self):
        """
        Validates the card status.
        Allowed values: active, inactive, expired
        """
        status = self.cleaned_data.get("status", "").lower()
        valid_statuses = {"active", "inactive", "expired"}
        if status not in valid_statuses:
            raise ValidationError("Status must be one of: active, inactive, expired")
        return status

    @staticmethod
    def _luhn_check(number: str) -> bool:
        """
        Performs a Luhn algorithm check on the card number.
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


class TransferValidationMixin(CardValidationMixin):
    """
    A mixin for validating Transfer model fields.
    Includes:
    - ext_id uniqueness (only on creation)
    - Currency validation (must be allowed)
    - Sender and receiver card validation
    - Balance and status checks
    - OTP validation with retry limit
    """

    def clean_ext_id(self):
        """
        Validates external transfer ID.
        Must not be empty and must be unique (if uniqueness check is enabled).
        """
        ext_id = self.cleaned_data.get("ext_id", "").strip()
        if not ext_id:
            raise ValidationError("External ID is required")

        if hasattr(self, 'check_ext_id_uniqueness') and self.check_ext_id_uniqueness:
            if Transfer.objects.filter(ext_id=ext_id).exists():
                raise ValidationError("External ID already exists")
        return ext_id

    def clean_currency(self):
        """
        Validates the currency.
        Only RUB (643) and USD (840) are allowed.
        """
        currency = self.cleaned_data.get("currency")
        if currency not in ALLOWED_CURRENCIES:
            raise ValidationError("Currency must be one of: 643 (RUB), 840 (USD)")
        return currency

    def clean_sending_amount(self):
        """
        Validates sending amount.
        Must be a positive number.
        """
        amount = self.cleaned_data.get("sending_amount")
        if not amount or Decimal(str(amount)) <= 0:
            raise ValidationError("Sending amount must be greater than zero")
        return Decimal(str(amount))

    def clean_sender_card_number(self):
        """
        Validates sender's card number using the Luhn check.
        """
        number = self.cleaned_data.get("sender_card_number", "")
        if not self._luhn_check(number):
            raise ValidationError("Invalid sender card number (failed Luhn check)")
        return number

    def clean_receiver_card_number(self):
        """
        Validates receiver's card number using the Luhn check.
        """
        number = self.cleaned_data.get("receiver_card_number", "")
        if not self._luhn_check(number):
            raise ValidationError("Invalid receiver card number (failed Luhn check)")
        return number

    def clean_sender_phone(self):
        """
        Validates sender phone number.
        Same rules as CardValidationMixin.clean_phone().
        """
        phone = str(self.cleaned_data.get("sender_phone", "")).strip()

        if not phone:
            return ""

        patterns = [
            r"^\+998\d{9}$",
            r"^\d{2}\s\d{3}\s\d{2}\s\d{2}$",
            r"^\d{3}-\d{2}-\d{2}$",
            r"^\d{9}$",
        ]
        if not any(re.fullmatch(p, phone) for p in patterns):
            raise ValidationError("Invalid phone number format")

        return phone

    def clean_receiver_phone(self):
        """
        Validates receiver phone number.
        Same rules as sender phone.
        """
        phone = str(self.cleaned_data.get("receiver_phone", "")).strip()

        if not phone:
            return ""

        patterns = [
            r"^\+998\d{9}$",
            r"^\d{2}\s\d{3}\s\d{2}\s\d{2}$",
            r"^\d{3}-\d{2}-\d{2}$",
            r"^\d{9}$",
        ]
        if not any(re.fullmatch(p, phone) for p in patterns):
            raise ValidationError("Invalid phone number format")

        return phone

    def clean_otp(self):
        """
        Validates OTP code for transfer confirmation.
        - Must be 6 digits
        - Checks against stored OTP in Transfer
        - Enforces maximum retry attempts
        """
        otp = self.cleaned_data.get("otp", "").strip()
        transfer_id = self.cleaned_data.get("transfer_id")

        if not otp:
            raise ValidationError("OTP code is required")

        if not otp.isdigit() or len(otp) != 6:
            raise ValidationError("OTP must be a 6-digit number")

        if transfer_id:
            try:
                transfer = Transfer.objects.get(id=transfer_id)

                if transfer.try_count >= MAX_OTP_ATTEMPTS:
                    raise ValidationError("Maximum OTP attempts exceeded")

                if str(transfer.otp) != str(otp):
                    transfer.try_count += 1
                    transfer.save(update_fields=['try_count'])

                    attempts_left = MAX_OTP_ATTEMPTS - transfer.try_count
                    raise ValidationError(f"Incorrect OTP. {attempts_left} attempts left")

            except Transfer.DoesNotExist:
                raise ValidationError("Transfer not found")

        return otp

    def clean(self):
        """
        Cross-field validations:
        - Sender card must exist and match expiry date
        - Receiver card must exist
        - Sender card must be active
        - Sender must have enough balance
        """
        cleaned = super().clean()
        sender_card_number = cleaned.get("sender_card_number")
        sender_card_expiry = cleaned.get("sender_card_expiry")
        receiver_card_number = cleaned.get("receiver_card_number")
        sending_amount = cleaned.get("sending_amount")

        if not all([sender_card_number, sender_card_expiry, receiver_card_number, sending_amount]):
            return cleaned

        try:
            sender = Card.objects.get(card_number=sender_card_number, expire=sender_card_expiry)
        except Card.DoesNotExist:
            raise ValidationError("Sender card not found or expiry date mismatch")

        try:
            receiver = Card.objects.get(card_number=receiver_card_number)
        except Card.DoesNotExist:
            raise ValidationError("Receiver card not found")

        if sender.status != "active":
            raise ValidationError("Sender card is not active")

        if sender.balance is None or sender.balance < Decimal(str(sending_amount)):
            raise ValidationError("Insufficient sender balance")

        self.sender = sender
        self.receiver = receiver

        return cleaned
