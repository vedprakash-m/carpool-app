from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """Enum for user roles in the system"""
    ADMIN = "admin"
    PARENT = "parent"
    STUDENT = "student"


class UserBase(BaseModel):
    """Base model for user data with common attributes"""
    email: EmailStr
    full_name: str
    phone_number: str
    home_address: str


class UserCreate(UserBase):
    """Model for user creation - includes password and role"""
    password: str
    role: UserRole


class User(UserBase):
    """Model for user response data with system fields"""
    id: UUID = Field(default_factory=uuid4)
    role: UserRole
    is_active_driver: bool = False
    hashed_password: str
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """Model for user data as stored in the database"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TokenData(BaseModel):
    """Model for JWT token data"""
    email: Optional[str] = None


class Token(BaseModel):
    """Model for authentication token response"""
    access_token: str
    token_type: str


class PasswordChangeRequest(BaseModel):
    """Model for password change requests"""
    current_password: str
    new_password: str


class AdminUserCreateRequest(UserBase):
    """Model for admin creating new users"""
    role: UserRole
    initial_password: str
