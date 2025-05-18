from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class VehicleType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    HATCHBACK = "hatchback"
    MINIVAN = "minivan"
    OTHER = "other"


class VehicleBase(BaseModel):
    """Base Vehicle model with common attributes"""
    owner_id: UUID
    make: str
    model: str
    year: int
    color: str
    license_plate: str
    vehicle_type: VehicleType
    seat_capacity: int
    features: Optional[str] = None


class VehicleCreate(VehicleBase):
    """Model for vehicle creation"""
    pass


class VehicleUpdate(BaseModel):
    """Model for updating vehicle information"""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    seat_capacity: Optional[int] = None
    features: Optional[str] = None


class VehicleInDB(VehicleBase):
    """Model for vehicle data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class Vehicle(VehicleBase):
    """Model for vehicle response data"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
