import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.car import router as car_router
from api.endpoints.payment import router as payment_router
from core.config import settings
from yookassa import Configuration as yookassaConfiguration

yookassaConfiguration.configure(settings.shop_id, settings.secret_token)

app = FastAPI(root_path="/api")

app.mount("/files/data", StaticFiles(directory="shared"), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(car_router, prefix="/car", tags=["Car Info"])
app.include_router(payment_router, prefix="/payment", tags=["Payments"])

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host,
                port=settings.port, reload=True)
