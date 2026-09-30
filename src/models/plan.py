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

class SubscriptionPlanUpdate(BaseModel):
    title: str
    description: str
    
    amount_usd: float
    duration_hours: int