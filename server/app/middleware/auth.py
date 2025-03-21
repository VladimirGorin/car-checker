from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from schemas.auth import AuthRequest
from services.user import get_user_by_id
from core.db import get_db
from sqlalchemy.orm import Session


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            if request.url.path.startswith("/api/user"):
                return await call_next(request)

            if request.url.path.startswith("/api/files"):
                return await call_next(request)

            body = await request.json()

            try:
                validated_data = AuthRequest(**body)
            except ValidationError as e:
                return JSONResponse(status_code=422, content={"detail": e.errors()})

            db: Session = next(get_db())

            try:
                user_id = body.get("user_id", "")
                get_user = get_user_by_id(db=db, user_id=user_id)

                if not get_user:
                    raise Exception("userId не корректный, или не найден")

            except Exception as e:
                return JSONResponse(status_code=400, content={"detail": str(e)})

            response = await call_next(request)
            response.headers["X-Custom-Header"] = "MiddlewareActive"

            return response
        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": str(e)})
