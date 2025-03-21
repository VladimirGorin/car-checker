from pydantic import BaseModel, Json
from typing import Any


class ReportBase(BaseModel):
    owner_id: str
    pdf_url: str
    data: Any


class ReportCreate(ReportBase):
    pass


class ReportSchema(BaseModel):
    id: int
    owner_id: str
    pdf_url: str
    data: Any

    class Config:
        from_attributes = True


class ReportsGetResponse(BaseModel):
    reports: list[ReportSchema]


class ReportsGetRequest(BaseModel):
    user_id: str
