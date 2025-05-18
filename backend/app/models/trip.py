from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TripStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RouteFrequency(str, Enum):
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TripBase(BaseModel):
    """Base Trip model with common attributes"""
    driver_id: UUID
    vehicle_id: UUID
    departure_location: str
    destination_location: str
    departure_time: datetime
    estimated_arrival_time: datetime
    available_seats: int
    price_per_seat: float
    frequency: RouteFrequency = RouteFrequency.ONE_TIME
    recurring_days: Optional[List[int]] = None  # Days of week (0-6, where 0 is Monday)
    notes: Optional[str] = None


class TripCreate(TripBase):
    """Model for trip creation"""
    pass


class TripUpdate(BaseModel):
    """Model for updating trip information"""
    vehicle_id: Optional[UUID] = None
    departure_location: Optional[str] = None
    destination_location: Optional[str] = None
    departure_time: Optional[datetime] = None
    estimated_arrival_time: Optional[datetime] = None
    available_seats: Optional[int] = None
    price_per_seat: Optional[float] = None
    status: Optional[TripStatus] = None
    frequency: Optional[RouteFrequency] = None
    recurring_days: Optional[List[int]] = None
    notes: Optional[str] = None


class TripInDB(TripBase):
    """Model for trip data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: TripStatus = TripStatus.SCHEDULED


class Trip(TripBase):
    """Model for trip response data"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: TripStatus

    class Config:
        from_attributes = True
