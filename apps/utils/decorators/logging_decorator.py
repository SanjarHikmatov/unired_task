import time
import json
import logging
from functools import wraps
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger('method_tracker')


def track_method(method_name=None, logger_name='method_tracker'):
    """
    Decorator that tracks and logs request/response data for important methods.

    Logs include:
        - Client IP address
        - Request body
        - Processing time in milliseconds
        - Response data or error details

    Features:
        - Detects JSON-RPC error responses automatically
        - Differentiates between success, error, and exception logs

    Args:
        method_name (str, optional): Custom method name for logging. Defaults to function name.
        logger_name (str, optional): Logger name to use. Default: 'method_tracker'

    Returns:
        function: Wrapped function with logging enabled
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            request = None
            ip_address = "unknown"

            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg
                    break

            if request:
                ip_address = get_client_ip(request)
                request_body = get_request_body(request)
            else:
                request_body = "No request object found"

            log_data = {
                'method': method_name or func.__name__,
                'ip_address': ip_address,
                'request_body': request_body,
                'timestamp': time.time()
            }

            logger.info(f"Start {log_data['method']} - IP: {ip_address}")

            try:
                result = func(*args, **kwargs)
                processing_time = round((time.time() - start_time) * 1000, 2)
                response_data = serialize_response(result)

                is_error = False
                try:
                    if isinstance(result, JsonResponse):
                        resp_json = json.loads(result.content.decode('utf-8'))
                        if 'error' in resp_json:
                            is_error = True
                except Exception:
                    pass

                if is_error:
                    logger.error(
                        f"Error {log_data['method']} - IP: {ip_address} - "
                        f"Time: {processing_time}ms - Response: {response_data[:500]}..."
                    )
                else:
                    logger.info(
                        f"Success {log_data['method']} - IP: {ip_address} - "
                        f"Time: {processing_time}ms - Response: {response_data[:500]}..."
                    )

                return result

            except Exception as e:
                processing_time = round((time.time() - start_time) * 1000, 2)
                logger.error(
                    f"Exception {log_data['method']} - IP: {ip_address} - "
                    f"Time: {processing_time}ms - Error: {str(e)}"
                )
                raise

        return wrapper

    return decorator


def get_client_ip(request):
    """
    Extract client IP address from request headers.

    Looks for:
        - X-Forwarded-For (proxy/load balancer)
        - REMOTE_ADDR (direct connection)

    Args:
        request (HttpRequest): The incoming request

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def get_request_body(request):
    """
    Safely extract request body data.

    - For form-encoded requests (POST), sensitive fields (password, otp, token) are removed.
    - For raw JSON/body requests, only first 500 characters are returned to avoid log bloat.

    Args:
        request (HttpRequest): The incoming request

    Returns:
        str: Extracted request body (sanitized if needed)
    """
    try:
        if hasattr(request, 'POST') and request.POST:
            filtered_data = {k: v for k, v in request.POST.items()
                             if k.lower() not in ['password', 'otp', 'token']}
            return json.dumps(filtered_data, default=str)
        elif hasattr(request, 'body') and request.body:
            return request.body.decode('utf-8')[:500]
        return "Empty request body"
    except Exception:
        return "Could not parse request body"


def serialize_response(response):
    """
    Safely serialize response data for logging.

    - Handles JsonResponse, objects, and plain strings.
    - Truncates to 500 characters to prevent huge logs.

    Args:
        response: Any response object or data

    Returns:
        str: Serialized response (safe for logs)
        
    """
    try:
        if hasattr(response, 'content'):
            return response.content.decode('utf-8')[:500]
        elif hasattr(response, '__dict__'):
            return str(response.__dict__)[:500]
        return str(response)[:500]
    except Exception:
        return "Could not serialize response"
