from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class NotificationType(str, Enum):
    TRIP_UPDATE = "trip_update"
    BOOKING_REQUEST = "booking_request"  
    BOOKING_CONFIRMATION = "booking_confirmation"
    TRIP_REMINDER = "trip_reminder"
    RATING_REQUEST = "rating_request"
    SYSTEM_MESSAGE = "system_message"


class NotificationBase(BaseModel):
    """Base Notification model with common attributes"""
    user_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    related_id: Optional[UUID] = None  # Trip ID, Booking ID, etc.


class NotificationCreate(NotificationBase):
    """Model for notification creation"""
    pass


class NotificationUpdate(BaseModel):
    """Model for updating notification information"""
    is_read: Optional[bool] = None


class NotificationInDB(NotificationBase):
    """Model for notification data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    is_read: bool = False


class Notification(NotificationBase):
    """Model for notification response data"""
    id: UUID
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True
