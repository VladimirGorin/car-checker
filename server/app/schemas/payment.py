from pydantic import BaseModel

class CreatePaymentRequest(BaseModel):
    amount: float

class GetPaymentRequest(BaseModel):
    payment_id: str
