import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.translation import gettext as _
from apps.transfers.forms.create_transaction_form import CreateTransferForm, ConfirmTransferForm, CancelTransferForm
from apps.transfers.models.transfer_models import Transfer
from apps.utils.models.errors_model import Error
from apps.utils.services import send_telegram_message, generate_otp

def create_jsonrpc_response(result=None, error=None, request_id=None):
    """Helper function to create JSON-RPC 2.0 response."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }

    if error:
        response["error"] = error
    else:
        response["result"] = result

    return response


def get_error_message(error_code, lang='en'):
    """Get localized error message by code."""
    try:
        error_obj = Error.objects.get(code=error_code)
        if lang == 'uz':
            return error_obj.uz
        elif lang == 'ru':
            return error_obj.ru
        else:
            return error_obj.en
    except Error.DoesNotExist:
        return f"Unknown error: {error_code}"


@csrf_exempt
@require_http_methods(["POST"])
def jsonrpc_handler(request):
    """Main JSON-RPC handler for all transfer operations."""
    try:
        data = json.loads(request.body)
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')

        if method in ['create', 'transfer.create']:
            return create_transfer_jsonrpc(params, request_id)
        elif method in ['confirm', 'transfer.confirm']:
            return confirm_transfer_jsonrpc(params, request_id)
        elif method in ['cancel', 'transfer.cancel']:
            return cancel_transfer_jsonrpc(params, request_id)
        else:
            error = {
                "code": -32601,
                "message": "Method not found",
                "data": f"Unknown method: {method}"
            }
            return JsonResponse(create_jsonrpc_response(error=error, request_id=request_id))

    except json.JSONDecodeError:
        error = {
            "code": -32700,
            "message": "Parse error",
            "data": "Invalid JSON"
        }
        return JsonResponse(create_jsonrpc_response(error=error))
    except Exception as e:
        error = {
            "code": -32603,
            "message": "Internal error",
            "data": str(e)
        }
        return JsonResponse(create_jsonrpc_response(error=error, request_id=data.get('id')))


def create_transfer_jsonrpc(params, request_id):
    """JSON-RPC method for creating transfers."""
    form_data = {
        'sender_card_number': params.get('sender_card_numbere', params.get('sender_card_number', '')).replace(' ', ''),
        'sender_card_expiry': params.get('sender_card_expiry', ''),
        'receiver_card_number': params.get('receiver_card_number', '').replace(' ', ''),
        'sending_amount': params.get('sending_amount'),  # Map to sending_amount field (not amount)
        'currency': params.get('currency'),
        'sender_phone': params.get('sender_phone'),
        'receiver_phone': params.get('receiver_phone'),
    }

    if form_data['sender_phone'] and not form_data['sender_phone'].startswith('+'):
        form_data['sender_phone'] = '+' + form_data['sender_phone']
    if form_data['receiver_phone'] and not form_data['receiver_phone'].startswith('+'):
        form_data['receiver_phone'] = '+' + form_data['receiver_phone']

    form = CreateTransferForm(form_data)

    if form.is_valid():
        transfer = form.save()
        code = generate_otp()
        send_telegram_message(code)

        transfer.otp = code
        transfer.try_count = 0
        transfer.save()

        print(f"[v0] Generated OTP for transfer {transfer.id}: {code}")  # Debug log

        result = {
            "ext_id": transfer.ext_id,
            "state": transfer.state,
            "created_at": transfer.created_at.isoformat(),
            "sending_amount": str(transfer.sending_amount),
            "receiving_amount": str(params.get('receiving_amount', transfer.receiving_amount)),
            "currency": transfer.currency
        }
        return JsonResponse(create_jsonrpc_response(result=result, request_id=request_id))
    else:
        error_details = {}
        for field, errors in form.errors.items():
            error_details[field] = [str(error) for error in errors]

        error = {
            "code": 1001,
            "message": get_error_message(1001),
            "data": error_details
        }
        return JsonResponse(create_jsonrpc_response(error=error, request_id=request_id))

def confirm_transfer_jsonrpc(params, request_id):
    """JSON-RPC method for confirming transfers."""
    form = ConfirmTransferForm(params)

    if form.is_valid():
        transfer = form.transfer
        otp = form.cleaned_data['otp']

        if transfer.otp == otp:
            transfer.state = Transfer.State.CONFIRMED
            transfer.save()

            result = {
                "ext_id": transfer.ext_id,
                "state": transfer.state,
                "confirmed_at": timezone.now().isoformat()
            }
            return JsonResponse(create_jsonrpc_response(result=result, request_id=request_id))
        else:
            transfer.try_count += 1
            transfer.save()

            if transfer.try_count >= 3:
                transfer.state = Transfer.State.CANCELLED
                transfer.cancelled_at = timezone.now()
                transfer.save()

                error = {
                    "code": 1003,
                    "message": get_error_message(1003),
                    "data": {"ext_id": transfer.ext_id}
                }
            else:
                attempts_left = 3 - transfer.try_count
                error = {
                    "code": 1002,
                    "message": get_error_message(1002),
                    "data": {"attempts_left": attempts_left}
                }

            return JsonResponse(create_jsonrpc_response(error=error, request_id=request_id))
    else:
        error_details = {}
        for field, errors in form.errors.items():
            error_details[field] = [str(error) for error in errors]

        error = {
            "code": 1001,
            "message": get_error_message(1001),
            "data": error_details
        }
        return JsonResponse(create_jsonrpc_response(error=error, request_id=request_id))


def cancel_transfer_jsonrpc(params, request_id):
    """JSON-RPC method for cancelling transfers."""
    form = CancelTransferForm(params)

    if form.is_valid():
        transfer = form.transfer
        transfer.state = Transfer.State.CANCELLED
        transfer.cancelled_at = timezone.now()
        transfer.save()

        result = {
            "ext_id": transfer.ext_id,
            "state": transfer.state,
            "cancelled_at": transfer.cancelled_at.isoformat()
        }
        return JsonResponse(create_jsonrpc_response(result=result, request_id=request_id))
    else:
        error_details = {}
        for field, errors in form.errors.items():
            error_details[field] = [str(error) for error in errors]

        error = {
            "code": 1001,
            "message": get_error_message(1001),
            "data": error_details
        }
        return JsonResponse(create_jsonrpc_response(error=error, request_id=request_id))
