from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PARENT = "PARENT"
    STUDENT = "STUDENT"

class PreferenceLevel(str, Enum):
    PREFERRED = "PREFERRED"
    LESS_PREFERRED = "LESS_PREFERRED"
    UNAVAILABLE = "UNAVAILABLE"
    AVAILABLE_NEUTRAL = "AVAILABLE_NEUTRAL"

class AssignmentMethod(str, Enum):
    PREFERENCE_BASED = "PREFERENCE_BASED"
    HISTORICAL_BASED = "HISTORICAL_BASED"
    MANUAL = "MANUAL"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone_number: Optional[str] = None
    is_active_driver: bool = False
    home_address: Optional[str] = None

class UserCreate(UserBase):
    initial_password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    home_address: Optional[str] = None
    is_active_driver: Optional[bool] = None

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Child(BaseModel):
    id: str
    parent_id: str
    full_name: str
    grade: str
    school_id: str
    created_at: datetime
    updated_at: datetime

class Location(BaseModel):
    id: str
    name: str
    address: str
    type: str  # SCHOOL, PICKUP_POINT
    coordinates: dict  # {latitude: float, longitude: float}

class WeeklyScheduleTemplateSlot(BaseModel):
    id: str
    day_of_week: int  # 0 = Monday, 6 = Sunday
    start_time: str  # HH:MM format in local timezone
    end_time: str
    route_type: str  # SCHOOL_RUN, POINT_TO_POINT
    locations: List[str]  # Ordered list of location IDs
    max_capacity: int
    created_at: datetime
    updated_at: datetime

class DriverWeeklyPreference(BaseModel):
    id: str
    driver_parent_id: str
    week_start_date: date
    template_slot_id: str
    preference_level: PreferenceLevel
    submission_timestamp: datetime

class RideAssignment(BaseModel):
    id: str
    template_slot_id: str
    driver_parent_id: str
    assigned_date: date
    status: str  # SCHEDULED, COMPLETED, CANCELLED
    assignment_method: AssignmentMethod
    created_at: datetime
    updated_at: datetime

class SwapRequest(BaseModel):
    id: str
    requesting_driver_id: str
    requested_driver_id: str
    ride_assignment_id: str
    status: str  # PENDING, ACCEPTED, REJECTED
    created_at: datetime
    updated_at: datetime 