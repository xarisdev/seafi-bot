from pydantic import BaseModel

class ProductSchema(BaseModel):
    id: str
    title: str
    description: str | None
    offer_id: str
    offer_name: str
    offer_description: str | None

class PaymentSchema(BaseModel):
    invoice: dict
    subscription: dict

class InvoiceSchema(BaseModel):
    id: str
    status: str
    amountTotal: dict
    paymentUrl: str
    payment_timeout_s: int