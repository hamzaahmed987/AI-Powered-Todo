"""Utility decorators for API features.

Provides rate limiting, timeout, and other cross-cutting concerns.
"""

import time
import asyncio
from functools import wraps
from typing import Callable, Any
from collections import defaultdict

from app.utils.exceptions import ValidationError
from app.utils.logger import logger


# Rate limiting state: {function_name: [(timestamp, call_count)]}
_rate_limit_state = defaultdict(list)


def rate_limit(max_calls: int, time_window: int):
    """Decorator for rate limiting function calls.

    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds

    Example:
        @rate_limit(max_calls=10, time_window=60)
        def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        def _check_rate_limit(func_name: str) -> None:
            """Check and update rate limit state."""
            now = time.time()

            # Clean up old entries outside the time window
            _rate_limit_state[func_name] = [
                (timestamp, count)
                for timestamp, count in _rate_limit_state[func_name]
                if now - timestamp < time_window
            ]

            # Count calls in current window
            current_calls = sum(count for _, count in _rate_limit_state[func_name])

            if current_calls >= max_calls:
                logger.warning(
                    f"Rate limit exceeded for {func_name}: {current_calls}/{max_calls} calls"
                )
                raise ValidationError(
                    message=f"Rate limit exceeded. Maximum {max_calls} calls per {time_window} seconds",
                )

            # Record this call
            if _rate_limit_state[func_name]:
                _rate_limit_state[func_name][-1] = (
                    _rate_limit_state[func_name][-1][0],
                    _rate_limit_state[func_name][-1][1] + 1,
                )
            else:
                _rate_limit_state[func_name].append((now, 1))

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            _check_rate_limit(func.__name__)
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            _check_rate_limit(func.__name__)
            return func(*args, **kwargs)

        # Return async wrapper if function is async, else sync wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def timeout(seconds: int):
    """Decorator for enforcing function timeout.

    Args:
        seconds: Timeout in seconds

    Example:
        @timeout(seconds=3)
        async def my_async_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds,
                )
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds} seconds")
                raise ValidationError(
                    message=f"Operation timed out after {seconds} seconds",
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # For sync functions, just return the result as-is
            # (true timeout enforcement for sync is complex without threads)
            return func(*args, **kwargs)

        # Return async wrapper if function is async, else sync wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_call(func: Callable) -> Callable:
    """Decorator to log function calls.

    Args:
        func: Function to wrap

    Example:
        @log_call
        def my_function(x, y):
            return x + y
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise

    return wrapper
