from fastapi import APIRouter, Depends, HTTPException
from schemas.car import CarRequest, CarResponse, CreatePdfRequest
from services.car import get_car_limited_data, get_car_full_data, extract_car_images
from services.pdf import createPDF
from services.telegram import send_new_car_request
from services.report import create_report

from schemas.report import ReportCreate

from core.db import get_db

from sqlalchemy.orm import Session

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

    if request.subscription:
        report_data = response.get("message", {})

        base_dir = Path(f"./shared/{request.report_uuid}")
        image_dir = base_dir / "image"

        os.makedirs(image_dir, exist_ok=True)

        photos = report_data.get('content', {}).get(
            'content', {}).get("images", {}).get("photos", {})

        images = [img for img in photos.get('items', [])]

        await extract_car_images(images, image_dir)

        info_path = base_dir / "info.json"
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=4)

        await createPDF(report_data, request.report_uuid)

        report_pdf_url = f"data/{request.report_uuid}/report.pdf"

        report_data = ReportCreate(
            owner_id=request.user_id,
            pdf_url=report_pdf_url,
            data=report_data
        )

        db: Session = next(get_db())
        create_report(db=db, report_data=report_data)

        response.update({"pdf_url": report_pdf_url})

    return CarResponse(content=response)
