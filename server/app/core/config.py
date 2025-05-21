from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"

    car_api: str = "https://api-profi.avtocod.ru/rpc"
    api_password: str = ""
    api_login: str = ""

    yookassa_api: str = "https://api.yookassa.ru/v3/payments"
    payment_return_url: str = "https://check-car.pro/api" # https://check-car.pro/api http://0.0.0.0:8000
    shop_id: str = ""
    secret_token: str = ""

    telegram_bot_token: str = ""

    proxy: str = "http://cloakedheadland160712:iarGKEE8o5T4@94.142.141.165:14907"


    class Config:
        env_file = ".env"

settings = Settings()
