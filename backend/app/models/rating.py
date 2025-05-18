from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RatingType(str, Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"


class RatingBase(BaseModel):
    """Base Rating model with common attributes"""
    trip_id: UUID
    from_user_id: UUID
    to_user_id: UUID
    rating_type: RatingType
    score: int  # 1-5
    comment: Optional[str] = None


class RatingCreate(RatingBase):
    """Model for rating creation"""
    pass


class RatingUpdate(BaseModel):
    """Model for updating rating information"""
    score: Optional[int] = None
    comment: Optional[str] = None


class RatingInDB(RatingBase):
    """Model for rating data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Rating(RatingBase):
    """Model for rating response data"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
