from django import forms
from django.utils.translation import gettext_lazy as _
from apps.transfers.models.transfer_models import Transfer
from apps.utils.validations import TransferValidationMixin


class CreateTransferForm(TransferValidationMixin, forms.ModelForm):
    """
    Form for creating new transfers with comprehensive validation.
    Inherits validation logic from TransferValidationMixin.
    """

    class Meta:
        model = Transfer
        fields = [
            'sender_card_number',
            'sender_card_expiry',
            'receiver_card_number',
            'sender_phone',
            'receiver_phone',
            'sending_amount',
            'currency',
        ]

        widgets = {
            'sender_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890123456',
                'maxlength': '16'
            }),
            'sender_card_expiry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MM/YY or YYYY-MM'
            }),
            'receiver_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234567890123456',
                'maxlength': '16'
            }),
            'sender_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998901234567'
            }),
            'receiver_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998901234567'
            }),
            'sending_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'currency': forms.Select(
                choices=[(643, 'RUB'), (840, 'USD')],
                attrs={'class': 'form-control'}
            ),
        }

        labels = {
            'sender_card_number': _('Sender Card Number'),
            'sender_card_expiry': _('Sender Card Expiry'),
            'receiver_card_number': _('Receiver Card Number'),
            'sender_phone': _('Sender Phone'),
            'receiver_phone': _('Receiver Phone'),
            'sending_amount': _('Sending Amount'),
            'currency': _('Currency'),
        }

        help_texts = {
            'sender_card_expiry': _('Format: MM/YY or YYYY-MM'),
            'sender_phone': _('Phone number for OTP delivery'),
            'currency': _('643 for RUB, 840 for USD'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['sender_phone'].required = True

        self.fields['currency'].widget.choices = [
            (643, 'RUB - Russian Ruble'),
            (840, 'USD - US Dollar'),
        ]

    def save(self, commit=True):
        """
        Save the transfer with additional processing.
        Sets receiving_amount equal to sending_amount by default.
        """
        transfer = super().save(commit=False)

        if not transfer.receiving_amount:
            transfer.receiving_amount = transfer.sending_amount

        if commit:
            transfer.save()

        return transfer


class ConfirmTransferForm(forms.Form):
    """Form for confirming transfers with OTP."""

    ext_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'tr-uuid-here'
        }),
        label=_('External ID')
    )

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456',
            'maxlength': '6'
        }),
        label=_('OTP Code')
    )

    def clean_ext_id(self):
        ext_id = self.cleaned_data.get('ext_id')
        try:
            transfer = Transfer.objects.get(ext_id=ext_id)
            if transfer.state != Transfer.State.CREATED:
                raise forms.ValidationError(_('Transfer is not in created state'))
            self.transfer = transfer
            return ext_id
        except Transfer.DoesNotExist:
            raise forms.ValidationError(_('Transfer not found'))

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp or not otp.isdigit():
            raise forms.ValidationError(_('OTP must be 6 digits'))
        return otp


class CancelTransferForm(forms.Form):
    """Form for cancelling transfers."""

    ext_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'tr-uuid-here'
        }),
        label=_('External ID')
    )

    def clean_ext_id(self):
        ext_id = self.cleaned_data.get('ext_id')
        try:
            transfer = Transfer.objects.get(ext_id=ext_id)
            if transfer.state != Transfer.State.CREATED:
                raise forms.ValidationError(_('Only created transfers can be cancelled'))
            self.transfer = transfer
            return ext_id
        except Transfer.DoesNotExist:
            raise forms.ValidationError(_('Transfer not found'))
