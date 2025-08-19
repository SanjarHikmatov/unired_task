from django.urls import path
from . import views

urlpatterns = [
    path('jsonrpc/', views.jsonrpc_handler, name='transfer_jsonrpc'),
]