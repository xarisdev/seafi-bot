from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SubscriptionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: str
    user_id: int
    plan_id: int

    created_at: datetime
    started_at: datetime | None
    expires_at: datetime | None

    status: str