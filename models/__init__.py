"""
Models package initialization
"""

from .sales_conversation import (
    SalesConversation,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageRequest,
    MessageResponse,
)

__all__ = [
    "SalesConversation",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "MessageRequest",
    "MessageResponse",
]
