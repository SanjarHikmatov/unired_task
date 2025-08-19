from django import forms
from apps.cards.models.card import Card
from apps.utils.validations import CardValidationMixin


class CardForm(CardValidationMixin, forms.ModelForm):
    """
        CardForm is a Django ModelForm that handles user input for creating or updating Card objects.
        It extends `CardValidationMixin` to apply custom validation logic (e.g., checking card format or rules).

        Inherits:
            - CardValidationMixin: Provides extra validation methods for card data.
            - forms.ModelForm: Base class for creating forms directly from a Django model.

        Attributes (Meta):
            model (Card): The model this form is based on.
            fields (str): Specifies which model fields are included in the form.
                    '__all__' means all fields from the Card model are included.
    """

    class Meta:
        model: type[Card] = Card
        fields: str = '__all__'
