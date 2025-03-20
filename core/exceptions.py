import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError

logger = logging.getLogger('cine')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework that handles additional exceptions.
    """
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, ValidationError):
            response = Response({
                'error': 'Validation Error',
                'detail': exc.message,
            }, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, IntegrityError):
            response = Response({
                'error': 'Database Integrity Error',
                'detail': str(exc),
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f'Unhandled exception: {exc}', exc_info=True)
            response = Response({
                'error': 'Internal Server Error',
                'detail': 'An unexpected error occurred.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Log all errors
    logger.error(f'API Error: {exc}', exc_info=True,
                extra={
                    'view': context['view'].__class__.__name__,
                    'path': context['request'].path,
                    'method': context['request'].method,
                })

    return response 