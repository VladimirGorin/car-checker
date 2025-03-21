from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from schemas.report import ReportsGetRequest, ReportsGetResponse, ReportSchema
from services.report import get_reports_by_owner_id

router = APIRouter()


@router.post("/all", response_model=ReportsGetResponse)
async def get_all_reports(request: ReportsGetRequest, db: Session = Depends(get_db)):
    reports = get_reports_by_owner_id(db=db, owner_id=request.user_id)

    return ReportsGetResponse(reports=[ReportSchema.from_orm(report) for report in reports])
