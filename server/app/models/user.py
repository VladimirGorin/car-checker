import uuid
from sqlalchemy import Column, Integer, String
from core.db import Base
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
