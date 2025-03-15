# app/schemas.py
from pydantic import BaseModel

class CustomerSchema(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        orm_mode = True

class StripeWebhookData(BaseModel):
    object: dict

class StripeWebhookEvent(BaseModel):
    id: str
    type: str
    data: StripeWebhookData
    created: int
