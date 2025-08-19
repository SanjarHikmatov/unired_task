from rest_framework import serializers

class CardInfoRequestSerializer(serializers.Serializer):
    """
        Serializer for validating card information requests.

        This serializer is used to accept and validate card details
        before processing them (e.g., checking card info in payment systems).

        Fields:
            card_number (str): A string field that represents the card number.
                               Maximum length is 19 characters.
                               Example: '8600123456789012'
            expire (str): A string field that represents the card's expiration date.
                          Usually in MM/YY format. Example: '12/25'
    """
    card_number = serializers.CharField(max_length=19)
    expire = serializers.CharField(max_length=5)

# example usage
# data = {"card_number": "8600123412341234", "expire": "12/25"}
# serializer = CardInfoRequestSerializer(data=data)
#
# if serializer.is_valid():
#     print(serializer.validated_data)
# else:
#     print(serializer.errors)
