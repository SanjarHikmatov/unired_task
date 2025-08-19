from rest_framework import serializers

class CardInfoResponseSerializer(serializers.Serializer):
    card_status = serializers.CharField()
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    phone = serializers.CharField()
    masked_card = serializers.CharField()