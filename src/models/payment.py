from pydantic import BaseModel

class InvoiceSchema(BaseModel):
    id: str
    status: str
    amountTotal: dict
    paymentUrl: str
    payment_timeout_s: int