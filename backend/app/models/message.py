from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class MessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """Base Message model with common attributes"""
    sender_id: UUID
    receiver_id: UUID
    trip_id: Optional[UUID] = None
    content: str
    message_type: MessageType = MessageType.TEXT


class MessageCreate(MessageBase):
    """Model for message creation"""
    pass


class MessageUpdate(BaseModel):
    """Model for updating message information"""
    is_read: Optional[bool] = None


class MessageInDB(MessageBase):
    """Model for message data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = False


class Message(MessageBase):
    """Model for message response data"""
    id: UUID
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True
