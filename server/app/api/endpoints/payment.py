from fastapi import APIRouter, Depends, HTTPException
from schemas.payment import CreatePaymentRequest, GetPaymentRequest

from core.config import settings

from yookassa import Payment

import requests
import uuid

router = APIRouter()


@router.post("/create")
async def create_payment(request: CreatePaymentRequest):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": request.amount,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": settings.payment_return_url
        },
        "description": "Order No. 72"
    }, idempotence_key)

    return {"status": True, "message": payment}

@router.post("/get")
async def get_payment(request: GetPaymentRequest):
    payment = Payment.find_one(request.payment_id)

    return {"status": True, "message": payment}
