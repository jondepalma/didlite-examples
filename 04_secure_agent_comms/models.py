"""
Pydantic models for secure agent communication.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Message(BaseModel):
    """Structured message between agents."""
    sender: str = Field(..., description="Sender agent name (e.g., 'bob', 'alice')")
    recipient: str = Field(..., description="Recipient agent name")
    content: str = Field(..., description="Message content")
    timestamp: Optional[int] = Field(None, description="Unix timestamp (auto-added)")
    message_id: Optional[str] = Field(None, description="Unique message ID (auto-generated)")


class SignedMessage(BaseModel):
    """A cryptographically signed message with JWS token."""
    token: str = Field(..., description="JWS token containing signed message")
    sender_did: str = Field(..., description="Sender's DID for verification")


class VerifyRequest(BaseModel):
    """Request to verify a received message."""
    token: str = Field(..., description="JWS token to verify")


class VerifyResponse(BaseModel):
    """Response from message verification."""
    valid: bool = Field(..., description="Whether the signature is valid")
    payload: Optional[dict] = Field(None, description="Verified payload if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    sender_did: Optional[str] = Field(None, description="DID of the signer")


class AgentIdentity(BaseModel):
    """Agent identity information."""
    name: str = Field(..., description="Agent name")
    did: str = Field(..., description="Agent's DID")


class MessageHistory(BaseModel):
    """Message history for an agent."""
    agent: str = Field(..., description="Agent name")
    sent: List[dict] = Field(default_factory=list, description="Messages sent by this agent")
    received: List[dict] = Field(default_factory=list, description="Messages received by this agent")


class AttackScenario(BaseModel):
    """Attack scenario configuration."""
    attack_type: str = Field(..., description="Type of attack: 'replay', 'forge', 'intercept', 'token_theft', 'no_private_key'")
    target_agent: Optional[str] = Field(None, description="Target agent for the attack")
    stolen_token: Optional[str] = Field(None, description="Stolen token (for token_theft attack)")
