from pydantic import BaseModel

class SubscriptionPlanCreate(BaseModel):
    offer_id: str
    
    title: str
    description: str
    
    amount_usd: float
    duration_hours: int

class SubscriptionPlanRead(BaseModel):
    id: int
    offer_id: str
    
    title: str
    description: str

    amount_usd: float
    duration_hours: int

class SubscriptionUpdate(BaseModel):
    title: str = None
    description: str = None
    
    amount_usd: float = None
    duration_hours: int = None