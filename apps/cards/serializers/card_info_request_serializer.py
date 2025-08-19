from rest_framework import serializers

class CardInfoRequestSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=19)
    expire = serializers.CharField(max_length=5)