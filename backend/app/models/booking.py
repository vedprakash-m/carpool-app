from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingBase(BaseModel):
    """Base Booking model with common attributes"""
    trip_id: UUID
    passenger_id: UUID
    seats_booked: int = 1
    pickup_location: Optional[str] = None  # If different from trip departure


class BookingCreate(BookingBase):
    """Model for booking creation"""
    pass


class BookingUpdate(BaseModel):
    """Model for updating booking information"""
    seats_booked: Optional[int] = None
    pickup_location: Optional[str] = None
    status: Optional[BookingStatus] = None


class BookingInDB(BookingBase):
    """Model for booking data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: BookingStatus = BookingStatus.PENDING
    total_price: float


class Booking(BookingBase):
    """Model for booking response data"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: BookingStatus
    total_price: float

    class Config:
        from_attributes = True
