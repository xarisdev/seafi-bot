from typing import Any
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    status_code: int
    data: Any | None = None
    message: str | None = None