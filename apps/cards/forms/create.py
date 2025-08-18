from django import forms
from apps.cards.models.card import Card
from apps.utils.validations import CardValidationMixin


class CardForm(CardValidationMixin, forms.ModelForm):
    class Meta:
        model = Card
        fields = '__all__'