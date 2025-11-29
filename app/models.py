"""Data models for the Rowboat API SDK Connector."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RowboatCredentials(BaseModel):
    """Rowboat API credentials."""
    host: str = Field(..., description="Rowboat host URL (e.g., https://app.rowboatlabs.com)")
    api_key: str = Field(..., description="Rowboat API key")
    project_id: str = Field(..., description="Rowboat project ID")


class Message(BaseModel):
    """A chat message."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    credentials: RowboatCredentials = Field(..., description="Rowboat API credentials")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue an existing conversation")
    mock_tools: Optional[Dict[str, str]] = Field(None, description="Optional tool overrides for testing")
    stream: bool = Field(False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The assistant's response")
    conversation_id: str = Field(..., description="The conversation ID for continuing the conversation")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information if debug mode is enabled")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    rowboat_configured: bool = Field(..., description="Whether Rowboat is properly configured")


class OpenWebUIRequest(BaseModel):
    """Request model for OpenWebUI function execution."""
    credentials: RowboatCredentials = Field(..., description="Rowboat API credentials")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    debug: bool = Field(False, description="Enable debug mode for detailed logging")


class OpenWebUIResponse(BaseModel):
    """Response model for OpenWebUI function execution."""
    response: str = Field(..., description="The assistant's response")
    conversation_id: str = Field(..., description="The conversation ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
