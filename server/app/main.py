import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.car import router as car_router
from api.endpoints.user import router as user_router
from api.endpoints.payment import router as payment_router
from api.endpoints.report import router as report_router
from core.config import settings
from yookassa import Configuration as yookassaConfiguration

from middleware.auth import AuthMiddleware

from models import user, report
from core.db import engine, Base

yookassaConfiguration.configure(settings.shop_id, settings.secret_token)

app = FastAPI(root_path="/api")

Base.metadata.create_all(bind=engine)

app.mount("/files/data", StaticFiles(directory="shared"), name="files")

app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(car_router, prefix="/car", tags=["Car"])
app.include_router(payment_router, prefix="/payment", tags=["Payments"])
app.include_router(report_router, prefix="/report", tags=["Reports"])

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host,
                port=settings.port, reload=True)
