from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import logging

logger = logging.getLogger('cine')

def cache_response(timeout=None, key_prefix=''):
    """
    Cache the response of a view for a specified time.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            # Generate cache key based on the request
            cache_key = generate_cache_key(
                request,
                key_prefix,
                view_func.__name__,
                args,
                kwargs
            )

            # Try to get the response from cache
            response = cache.get(cache_key)
            if response is not None:
                logger.info(f'Cache hit for key: {cache_key}')
                return response

            # If not in cache, generate response
            logger.info(f'Cache miss for key: {cache_key}')
            response = view_func(self, request, *args, **kwargs)

            # Cache the response
            cache_timeout = timeout or settings.CACHE_TTL
            cache.set(cache_key, response, cache_timeout)

            return response
        return _wrapped_view
    return decorator

def generate_cache_key(request, prefix, view_name, args, kwargs):
    """
    Generate a unique cache key based on the request parameters.
    """
    # Create a string with all the components that make the request unique
    key_components = [
        prefix,
        view_name,
        request.path,
        request.method,
        str(request.GET),
        str(args),
        str(kwargs)
    ]

    if hasattr(request, 'user') and request.user.is_authenticated:
        key_components.append(str(request.user.id))

    # Join all components and create a hash
    key_string = ':'.join(key_components)
    return hashlib.md5(key_string.encode()).hexdigest() 