from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from core.db import SessionLocal, get_db

from schemas.user import UserCreateRequest, UserCreateResponse

from services.user import create_user

from pathlib import Path

import os
import json

router = APIRouter()


@router.get("/create", response_model=UserCreateResponse)
async def create_new_user(db: Session = Depends(get_db)):
    user_data = UserCreateRequest()
    new_user = create_user(db=db, user_data=user_data)

    return new_user
