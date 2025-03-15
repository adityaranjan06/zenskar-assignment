# app/schemas.py
from pydantic import BaseModel

class CustomerSchema(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        orm_mode = True

class CustomerUpdateSchema(BaseModel):
    name: str
    email: str

class StripeWebhookData(BaseModel):
    object: dict

class StripeWebhookEvent(BaseModel):
    id: str
    type: str
    data: StripeWebhookData
    created: int
