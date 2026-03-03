import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('reservations')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(
            "API Error: %s | Path: %s | Status: %s",
            str(exc),
            context['request'].path,
            response.status_code,
        )
        # Normalize error shape
        if isinstance(response.data, dict) and 'detail' not in response.data:
            response.data = {'detail': response.data}
    else:
        logger.exception("Unhandled exception in %s", context['view'].__class__.__name__)

    return response
