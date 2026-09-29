from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    telegram_id: int

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    trial_expires_at: datetime
    created_at: datetime