from django.urls import path
from apps.cards.views import CardInfoView

urlpatterns = [
    path('card-info/', CardInfoView.as_view(), name='card-info')
]