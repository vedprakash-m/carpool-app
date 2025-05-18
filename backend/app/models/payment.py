from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    CASH = "cash"
    OTHER = "other"


class PaymentBase(BaseModel):
    """Base Payment model with common attributes"""
    booking_id: UUID
    amount: float
    payment_method: PaymentMethod
    transaction_reference: Optional[str] = None  # External payment reference


class PaymentCreate(PaymentBase):
    """Model for payment creation"""
    pass


class PaymentUpdate(BaseModel):
    """Model for updating payment information"""
    status: Optional[PaymentStatus] = None
    transaction_reference: Optional[str] = None


class PaymentInDB(PaymentBase):
    """Model for payment data as stored in the database"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: PaymentStatus = PaymentStatus.PENDING


class Payment(PaymentBase):
    """Model for payment response data"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: PaymentStatus

    class Config:
        from_attributes = True
