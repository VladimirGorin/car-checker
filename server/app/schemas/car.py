from pydantic import BaseModel
from typing import Optional

class CarRequest(BaseModel):
    query: str
    subscription: bool
    car_type: str
    report_uuid: Optional[str] = None

class CarResponse(BaseModel):
    content: object

class CreatePdfRequest(BaseModel):
    data: object
    report_uuid: str
