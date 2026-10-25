from enum import Enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    created_at: datetime

class Plan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    offer_id: str
    title: str
    description: str
    amount: float
    duration: int
    created_at: datetime

class PlanCreate(BaseModel):
    offer_id: str
    title: str
    description: str
    amount: float
    duration: int

class PlanUpdate(BaseModel):
    title: str
    description: str
    amount: float
    duration: int


class Invoice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int
    user_id: int
    contract_id: str
    payment_url: str
    status: str
    currency: str
    amount_total: str
    created_at: datetime

class EnumInvoiceStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class LavaProduct(BaseModel):
    id: str | None
    title: str
    description: str | None
    offer_id: str
    offer_name: str | None
    offer_description: str | None


class Subscription(BaseModel):
    id: int
    user_id: int
    plan_id: int | None
    invoice_id: int | None
    created_at: datetime
    started_at: datetime | None
    expires_at: datetime | None
    source: str


class WebSocketMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    buyer_email: str
    contract_id: str
    invoice_status: str

    created_at: datetime | None = None