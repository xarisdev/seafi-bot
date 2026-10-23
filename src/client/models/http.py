from typing import Any
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    status_code: int | None
    response_json: Any | None
    response_details: Any | None