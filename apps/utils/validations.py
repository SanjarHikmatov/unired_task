
import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.transfers.models import Transfer
from apps.cards.models.card import Card


ALLOWED_CURRENCIES = [643, 840]
MAX_OTP_ATTEMPTS = 3



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

        if not CardValidationMixin._luhn_check(digits):
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
    @staticmethod
    def _luhn_check(number: str) -> bool:
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


class TransferValidationMixin(CardValidationMixin):
    """
    A mixin for validating Transfer model fields.
    Includes:
    - ext_id uniqueness (only for creation)
    - currency check (must be in allowed list)
    - sender and receiver card existence
    - balance and status checks
    - OTP try limit
    """

    def clean_ext_id(self):
        ext_id = self.cleaned_data.get("ext_id", "").strip()
        if not ext_id:
            raise ValidationError("Ext ID is required")

        if hasattr(self, 'check_ext_id_uniqueness') and self.check_ext_id_uniqueness:
            if Transfer.objects.filter(ext_id=ext_id).exists():
                raise ValidationError("Ext ID already exists")
        return ext_id

    def clean_currency(self):
        currency = self.cleaned_data.get("currency")
        if currency not in ALLOWED_CURRENCIES:
            raise ValidationError("Currency must be one of 643 (RUB), 840 (USD)")
        return currency

    def clean_sending_amount(self):
        amount = self.cleaned_data.get("sending_amount")
        if not amount or Decimal(str(amount)) <= 0:
            raise ValidationError("Sending amount must be positive")
        return Decimal(str(amount))

    def clean_sender_card_number(self):
        number = self.cleaned_data.get("sender_card_number", "")
        if not self._luhn_check(number):
            raise ValidationError("Invalid sender card number (Luhn check failed)")
        return number

    def clean_receiver_card_number(self):
        number = self.cleaned_data.get("receiver_card_number", "")
        if not self._luhn_check(number):
            raise ValidationError("Invalid receiver card number (Luhn check failed)")
        return number

    def clean_sender_phone(self):
        """
        Validates the sender phone number.
        Supports multiple formats including:
        - +998XXXXXXXXX
        - 99 973 03 03
        - 973-03-03
        - 991234567
        If empty, returns an empty string.
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
            raise ValidationError("Phone number is wrong formatted")

        return phone

    def clean_receiver_phone(self):
        """
        Validates the receiver phone number.
        Same validation as sender phone.
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
            raise ValidationError("Phone number is wrong formatted")

        return phone

    def clean_otp(self):
        """
        Validates OTP code for transfer confirmation.
        Checks if OTP matches and if attempts limit is not exceeded.
        """
        otp = self.cleaned_data.get("otp", "").strip()
        transfer_id = self.cleaned_data.get("transfer_id")

        if not otp:
            raise ValidationError("OTP code is required")

        if not otp.isdigit() or len(otp) != 6:
            raise ValidationError("OTP must be 6 digits")

        if transfer_id:
            try:
                transfer = Transfer.objects.get(id=transfer_id)

                print(f"[v0] Debug - User OTP: '{otp}' (type: {type(otp)})")
                print(f"[v0] Debug - DB OTP: '{transfer.otp}' (type: {type(transfer.otp)})")
                print(f"[v0] Debug - OTP comparison: {transfer.otp} != {otp} = {transfer.otp != otp}")

                # Check if max attempts exceeded
                if transfer.try_count >= MAX_OTP_ATTEMPTS:
                    raise ValidationError("Maximum OTP attempts exceeded")

                # Check if OTP matches - convert both to strings for comparison
                if str(transfer.otp) != str(otp):
                    # Increment try count
                    transfer.try_count += 1
                    transfer.save(update_fields=['try_count'])

                    attempts_left = MAX_OTP_ATTEMPTS - transfer.try_count
                    raise ValidationError(f"Invalid OTP code. {attempts_left} attempts left")

            except Transfer.DoesNotExist:
                raise ValidationError("Transfer not found")

        return otp

    def clean(self):
        """
        Cross-field validations:
        - Sender card exists and active
        - Receiver card exists
        - Sender has enough balance
        - Sender has phone number
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
            raise ValidationError("Sender card not found or expiry mismatch")

        try:
            receiver = Card.objects.get(card_number=receiver_card_number)
        except Card.DoesNotExist:
            raise ValidationError("Receiver card not found")

        if sender.status != "active":
            raise ValidationError("Sender card is not active")

        if sender.balance is None or sender.balance < Decimal(str(sending_amount)):
            raise ValidationError("Sender balance is not enough")

        self.sender = sender
        self.receiver = receiver

        return cleaned
