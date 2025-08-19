from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from apps.cards.models import Card
from apps.cards.serializers import CardInfoRequestSerializer, CardInfoResponseSerializer
from apps.utils.decorators.logging_decorator import track_method


class CardInfoView(APIView):
    @track_method('post')
    def post(self, request):
        """
            Handle POST request to retrieve card information.

            Steps:
            1. Validate input using CardInfoRequestSerializer.
            2. Check cache for existing card info.
            3. If cached, return cached data.
            4. Query the database for the card by card_number and expire date.
            5. If found, mask the card number and return status, balance, phone, and masked_card.
            6. Cache the response for 30 seconds to reduce DB load.
            7. If not found, return a 404 error and cache the error response.
        """
        serializer = CardInfoRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        card_number = serializer.validated_data['card_number']
        expire = serializer.validated_data['expire']
        cache_key = f"card_info:{card_number}:{expire}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        try:
            card = Card.objects.get(card_number=card_number, expire=expire)
            response_data = {
                "card_status": card.status,
                "balance": card.balance,
                "phone": card.phone,
                "masked_card": f"{card.card_number[:6]}******{card.card_number[-4:]}"
            }

            cache.set(cache_key, response_data, timeout=30)

            response_serializer = CardInfoResponseSerializer(response_data)
            return Response(response_serializer.data)

        except Card.DoesNotExist:
            error_response = {"error": "Card not found"}
            cache.set(cache_key, error_response, timeout=30)
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)
