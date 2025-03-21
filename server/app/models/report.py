import uuid
from sqlalchemy import Column, Integer, String, JSON, VARCHAR
from core.db import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String(36), nullable=False)
    pdf_url = Column(VARCHAR, nullable=False)
    data = Column(JSON, nullable=False)
