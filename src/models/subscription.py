from pydantic import BaseModel

class SubscriptionCreate(BaseModel):
    offer_id: str
    title: str
    description: str

    amount_usd: float

    duration_h: int

class SubscriptionRead(BaseModel):
    id: int
    offer_id: str
    title: str
    description: str
    amount_usd: float
    duration_h: int

class SubscriptionUpdate(BaseModel):
    id: int
    title: str = None
    description: str = None
    
    amount_usd: float = None

    duration_h: int = None