from pydantic import BaseModel

class PaymentSchema(BaseModel):
    id: str
    status: str
    amountTotal: dict
    paymentUrl: str
    payment_timeout_s: int