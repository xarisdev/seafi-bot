from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Payload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_id: int
    invoice_id: str
    event_status: str
    status: str
    timestamp: datetime
    subscription_id: int
    subscription_range: dict[str, datetime]