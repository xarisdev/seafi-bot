from pydantic import BaseModel

from .subscription import SubscriptionSchema

class ProductSchema(BaseModel):
    id: str
    title: str
    description: str | None
    offer_id: str
    offer_name: str
    offer_description: str | None

class InvoiceSchema(BaseModel):
    id: str
    status: str
    amountTotal: dict
    paymentUrl: str
    payment_timeout_s: int

class PaymentSchema(BaseModel):
    invoice: InvoiceSchema
    subscription: SubscriptionSchema