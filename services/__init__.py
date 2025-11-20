"""Service layer for the conversational Course Builder API."""

from .conversation_manager import ConversationManager, conversation_manager
from .config import settings

__all__ = ["ConversationManager", "conversation_manager", "settings"]

