import uuid

from django.db import models
from django.utils import timezone
from apps.utils.models.base_model import BaseModel
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, RegexValidator


class Transfer(BaseModel):
    class State(models.TextChoices):
        CREATED = "created", _("created")
        CONFIRMED = "confirmed", _("confirmed")
        CANCELLED = "cancelled", _("cancelled")

    ext_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name=_("External ID"),
    )

    sender_card_number = models.CharField(
        max_length=16,
        db_index=True,
        verbose_name=_("Sender card number"),
    )
    receiver_card_number = models.CharField(
        max_length=16,
        db_index=True,
        verbose_name=_("Receiver card number"),
    )

    sender_card_expiry = models.CharField(
        max_length=7,
        help_text=_("MM/YY or YYYY-MM"),
        validators=[RegexValidator(r"^(\d{2}/\d{2}|\d{4}-\d{2})$", _("Expiry format is invalid"))],
        verbose_name=_("Sender card expiry"),
    )

    sender_phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name=_("Sender phone"),
    )
    receiver_phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name=_("Receiver phone"),
    )

    sending_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Sending amount"),
    )

    currency = models.PositiveIntegerField(
        verbose_name=_("Currency"),
    )

    receiving_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("Receiving amount"),
    )

    state = models.CharField(
        max_length=10,
        choices=State.choices,
        default=State.CREATED,
        verbose_name=_("State"),
    )

    try_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Try count"),
    )
    otp = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name=_("OTP"),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created at"),
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Confirmed at"),
    )
    cancelled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Cancelled at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
    )

    class Meta:
        db_table = "transfers"
        indexes = [
            models.Index(fields=["sender_card_number"]),
            models.Index(fields=["receiver_card_number"]),
            models.Index(fields=["state", "created_at"]),
        ]
        verbose_name = _("Transfer")
        verbose_name_plural = _("Transfers")

    def __str__(self):
        return f"Transfer({self.ext_id}, state={self.state})"
