"""Service layer for interacting with Rowboat SDK."""
import logging
from typing import List, Optional, Dict, Any
from rowboat.client import Client
from rowboat.schema import UserMessage, AssistantMessage, SystemMessage

from app.config import Settings
from app.models import Message

logger = logging.getLogger(__name__)


class RowboatService:
    """Service for managing Rowboat SDK interactions."""

    def __init__(self, settings: Settings):
        """Initialize the Rowboat service.

        Args:
            settings: Application settings containing Rowboat configuration
        """
        self.settings = settings
        self.client = Client(
            host=settings.rowboat_host,
            projectId=settings.rowboat_project_id,
            apiKey=settings.rowboat_api_key
        )
        logger.info(
            f"Rowboat client initialized with host={settings.rowboat_host}, "
            f"project_id={settings.rowboat_project_id}"
        )

    def _convert_to_rowboat_messages(self, messages: List[Message]) -> List[Any]:
        """Convert generic messages to Rowboat message format.

        Args:
            messages: List of generic messages

        Returns:
            List of Rowboat message objects
        """
        rowboat_messages = []
        for msg in messages:
            if msg.role.lower() == "user":
                rowboat_messages.append(UserMessage(role="user", content=msg.content))
            elif msg.role.lower() == "assistant":
                rowboat_messages.append(AssistantMessage(role="assistant", content=msg.content))
            elif msg.role.lower() == "system":
                rowboat_messages.append(SystemMessage(role="system", content=msg.content))
            else:
                # Default to user message
                rowboat_messages.append(UserMessage(role="user", content=msg.content))
        return rowboat_messages

    def run_turn(
        self,
        messages: List[Message],
        conversation_id: Optional[str] = None,
        mock_tools: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Run a conversation turn with Rowboat.

        Args:
            messages: List of messages in the conversation
            conversation_id: Optional conversation ID to continue existing conversation
            mock_tools: Optional tool overrides for testing

        Returns:
            Dictionary containing response and conversation_id
        """
        try:
            # Convert messages to Rowboat format
            rowboat_messages = self._convert_to_rowboat_messages(messages)

            if self.settings.debug:
                logger.debug(f"Running turn with {len(rowboat_messages)} messages")
                logger.debug(f"Conversation ID: {conversation_id}")
                logger.debug(f"Mock tools: {mock_tools}")

            # Run the turn
            result = self.client.run_turn(
                messages=rowboat_messages,
                conversationId=conversation_id,
                mockTools=mock_tools
            )

            # Extract response
            response_content = ""
            if result.turn.output:
                response_content = result.turn.output[-1].content

            debug_info = None
            if self.settings.debug:
                debug_info = {
                    "conversation_id": result.conversationId,
                    "turn_output_count": len(result.turn.output) if result.turn.output else 0,
                    "messages_sent": len(rowboat_messages),
                }
                logger.debug(f"Debug info: {debug_info}")

            return {
                "response": response_content,
                "conversation_id": result.conversationId,
                "debug_info": debug_info
            }

        except Exception as e:
            logger.error(f"Error running turn: {str(e)}", exc_info=True)
            raise

    def health_check(self) -> bool:
        """Check if the Rowboat service is healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Simple validation that client is configured
            return (
                self.client is not None
                and self.settings.rowboat_host
                and self.settings.rowboat_api_key
                and self.settings.rowboat_project_id
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
