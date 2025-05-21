import requests
import aiohttp
import asyncio
import os, json
from core.config import settings

from services.telegram import send_proxy_error_request

url = settings.car_api
proxies = {
    "http": settings.proxy,
    "https": settings.proxy,
}


import aiohttp

async def get_auth_token(login, password) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": "https://profi.avtocod.ru/",
        "Origin": "https://profi.avtocod.ru/"
    }

    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "auth.login",
        "params": {"email": login, "password": password},
    }


    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers, proxy=settings.proxy) as response:
                response_text = await response.text()
                try:
                    response_json = json.loads(response_text)
                except json.JSONDecodeError:
                    raise aiohttp.ContentTypeError(request_info=response.request_info, history=response.history, message="Invalid JSON")

                response_error = response_json.get("error")

                if response_error:
                    raise Exception(str(response_error))

                return response_json.get("result", {}).get("token", "")

        except aiohttp.ContentTypeError:
            send_proxy_error_request(f"Ошибка JSON в get_auth_token: {response_text}")
        except aiohttp.ClientConnectionError:
            send_proxy_error_request("Ошибка соединения с прокси в get_auth_token: Невозможно подключиться к прокси. (Проверьте прокси)")
        except aiohttp.ClientError as e:
            send_proxy_error_request(f"Ошибка запроса в get_auth_token: {e}")
        except Exception as e:
            send_proxy_error_request(f"Ошибка запроса в get_auth_token: {e}")

    return ""


async def create_car_report_uuid(car_type: str, query: str) -> str | None:
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)
    print("ACCESS_TOKEN", ACCESS_TOKEN)
    if not ACCESS_TOKEN:
        return None

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Referer": "https://profi.avtocod.ru/",
        "Origin": "https://profi.avtocod.ru/"
    }

    data = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "report.create",
        "params": {"query": query, "type": car_type},
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers, proxy=settings.proxy) as response:
                response_json = await response.json()
                return response_json.get("result", {}).get("uuid", "")
        except aiohttp.ContentTypeError:
            print(f"Ошибка JSON в create_car_report_uuid: {await response.text()}")
        except aiohttp.ClientError as e:
            print(f"Ошибка запроса в create_car_report_uuid: {e}")
    return None


async def get_car_limited_data(car_type: str, query: str) -> object:
    REPORT_UUID = await create_car_report_uuid(car_type, query)
    if not REPORT_UUID:
        return {"status": False, "message": "Ошибка создания отчёта"}

    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)
    if not ACCESS_TOKEN:
        return {"status": False, "message": "Ошибка аутентификации"}

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Referer": "https://profi.avtocod.ru/",
        "Origin": "https://profi.avtocod.ru/"
    }

    data = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "report.get",
        "params": {"uuid": REPORT_UUID},
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers, proxy=settings.proxy) as response:
                response_json = await response.json()
                error = response_json.get("error", {})
                if error:
                    return {"status": False, "message": f"Ошибка! {error}"}
                return {"status": True, "message": response_json.get("result", response_json)}
        except aiohttp.ContentTypeError:
            print(f"Ошибка JSON в get_car_limited_data: {await response.text()}")
        except aiohttp.ClientError as e:
            print(f"Ошибка запроса в get_car_limited_data: {e}")
    return {"status": False, "message": "Ошибка при получении данных"}


async def update_car_report(report_uuid: str) -> None:
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)
    if not ACCESS_TOKEN:
        return

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Referer": "https://profi.avtocod.ru/",
        "Origin": "https://profi.avtocod.ru/"
    }

    data = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "report.upgrade",
        "params": {
            "uuid": report_uuid,
        }
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
        try:
            async with session.post(url, json=data, headers=headers, proxy=settings.proxy) as response:
                response_json = await response.json()
                time_to_sleep = response_json.get("result", {}).get(
                    "max_wait_to_ready_time", 0
                ) * 2

                print("time_to_sleep", time_to_sleep)
                await asyncio.sleep(time_to_sleep)
        except aiohttp.ContentTypeError:
            print(f"Ошибка JSON в update_car_report: {await response.text()}")
        except aiohttp.ClientError as e:
            print(f"Ошибка запроса в update_car_report: {e}")


async def get_car_full_data(report_uuid: str) -> object:
    await update_car_report(report_uuid)
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)

    if not ACCESS_TOKEN:
        return {"status": False, "message": "Ошибка аутентификации"}

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Referer": "https://profi.avtocod.ru/",
        "Origin": "https://profi.avtocod.ru/"
    }

    data = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "report.get",
        "params": {"uuid": report_uuid},
    }

    try:
        response = requests.post(
            url, json=data, headers=headers, proxies=proxies)
        response.raise_for_status()
        response_json = response.json()
        error = response_json.get("error", {})

        if error:
            return {"status": False, "message": f"Ошибка! {error}"}

        return {"status": True, "message": response_json.get("result", response_json)}
    except requests.exceptions.JSONDecodeError:
        print(f"Ошибка JSON в get_car_full_data: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса в get_car_full_data: {e}")

    return {"status": False, "message": "Ошибка при получении данных"}

async def download_image(session, url: str, save_path: str, index: int):
    filename = os.path.join(save_path, f"{index}.jpg")

    try:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filename, "wb") as f:
                    f.write(await response.read())
            else:
                print(f"Ошибка загрузки {url}: {response.status}")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")

async def extract_car_images(images: list, save_path: str):
    if not isinstance(images, list):
        return

    os.makedirs(save_path, exist_ok=True)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
        tasks = [
            download_image(session, img['uri'], save_path, idx)
            for idx, img in enumerate(images) if isinstance(img, dict) and 'uri' in img
        ]
        await asyncio.gather(*tasks)
