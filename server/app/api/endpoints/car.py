from fastapi import APIRouter, Depends, HTTPException
from schemas.car import CarRequest, CarResponse, CreatePdfRequest
from services.car import get_car_limited_data, get_car_full_data, extract_car_images
from services.pdf import createPDF
from services.telegram import send_new_car_request

from pathlib import Path
import os
import json

router = APIRouter()


@router.post("/info", response_model=CarResponse)
async def get_car_data(request: CarRequest):
    response = {}

    if request.subscription:
        if (not request.report_uuid):
            raise HTTPException(
                status_code=400, detail=f"Поле корректны запрос")

        response = await get_car_full_data(request.report_uuid)
    else:
        response = await get_car_limited_data(request.car_type, request.query)

    if response.get("status") is False:
        raise HTTPException(
            status_code=400, detail=f"Не корректный запрос {response}")

    message = f"Тип: {request.car_type}\n\nЗапрос: {request.query}\n\nСтатус: {'Полный отчет' if request.subscription else 'Неполный отчет'}"
    send_new_car_request(message)

    return CarResponse(content=response)


@router.post("/create-pdf")
async def create_pdf(request: CreatePdfRequest):

    base_dir = Path(f"./shared/{request.report_uuid}")
    image_dir = base_dir / "image"

    os.makedirs(image_dir, exist_ok=True)

    photos = request.data.get('result', {}).get('content', {}).get('content', {}).get("images", {}).get("photos", {})

    images = [img for img in photos.get('items', [])]

    # print("images", images)

    await extract_car_images(images, image_dir)

    info_path = base_dir / "info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(request.data, f, ensure_ascii=False, indent=4)

    await createPDF(request.data, request.report_uuid)

    return {"status": True, "message": f"data/{request.report_uuid}/report.pdf"}
