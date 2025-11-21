"""
System constants package for the sales API.
"""

from .system_messages import (
    SYSTEM_MESSAGE_TYPES,
    SALES_WELCOME_MESSAGES,
    get_random_welcome_message,
    get_system_message_response
)

__all__ = [
    'SYSTEM_MESSAGE_TYPES',
    'SALES_WELCOME_MESSAGES',
    'get_random_welcome_message',
    'get_system_message_response'
]
