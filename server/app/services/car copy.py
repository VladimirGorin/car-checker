import requests, aiohttp, asyncio, os
from core.config import settings

url = settings.car_api

async def get_auth_token(login, password) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Origin": "https://profi.avtocod.ru",
        "Connection": "keep-alive",
        "Referer": "https://profi.avtocod.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0",
        "TE": "trailers",
    }

    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "auth.login",
        "params": {
            "email": login, "password": password
        }
    }

    response = requests.post(url, json=data, headers=headers).json()
    print("get_auth_token_response", response)

    return response.get("result", {}).get("token", "")


async def create_car_report_uuid(car_type: str, query: str) -> str | None:
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Origin": "https://profi.avtocod.ru",
        "Connection": "keep-alive",
        "Referer": "https://profi.avtocod.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0",
        "TE": "trailers",
    }

    data = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "report.create",
        "params": {
            "query": query,
            "type": car_type
        }
    }

    response = requests.post(url, json=data, headers=headers).json()

    print("create_car_report_uuid_response", response)

    return response.get("result", {}).get("uuid", "")


async def update_car_report(report_uuid: str) -> None:
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Origin": "https://profi.avtocod.ru",
        "Connection": "keep-alive",
        "Referer": "https://profi.avtocod.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0",
        "TE": "trailers",
    }

    data = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "report.upgrade",
        "params": {
            "uuid": report_uuid,
        }
    }

    print("report_uuid", report_uuid)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            response_json = await response.json()

    time_to_sleep = response_json.get("result", {}).get("max_wait_to_ready_time", 0) * 2

    print("time_to_sleep", time_to_sleep)

    await asyncio.sleep(time_to_sleep)

    print("update_car_report_response", response_json)


async def get_car_limited_data(car_type: str, query: str) -> object:
    result = {}

    REPORT_UUID = await create_car_report_uuid(car_type, query)
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)

    print("REPORT_UUID", REPORT_UUID)
    print("\n")
    print("ACCESS_TOKEN", ACCESS_TOKEN)
    print("\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Origin": "https://profi.avtocod.ru",
        "Connection": "keep-alive",
        "Referer": "https://profi.avtocod.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0",
        "TE": "trailers",
    }

    data = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "report.get",
        "params": {
            "uuid": REPORT_UUID
        }
    }

    response = requests.post(url, json=data, headers=headers).json()
    print(f"RESPONSE: {response}")
    error = response.get("error", {})

    # print(error)
    if len(error):
        error_code = error.get("code")

        result = {"status": False, "message": f"Ошибка! {error}"}
    else:
        result = {"status": True, "message": response.get("result", response)}

    return result


async def get_car_full_data(report_uuid: str) -> object:
    result = {}

    await update_car_report(report_uuid)
    ACCESS_TOKEN = await get_auth_token(settings.api_login, settings.api_password)

    # print("REPORT_UUID", REPORT_UUID)
    # print("\n")
    # print("ACCESS_TOKEN", ACCESS_TOKEN)
    # print("\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Origin": "https://profi.avtocod.ru",
        "Connection": "keep-alive",
        "Referer": "https://profi.avtocod.ru/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=0",
        "TE": "trailers",
    }

    data = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "report.get",
        "params": {
            "uuid": report_uuid
        }
    }

    response = requests.post(url, json=data, headers=headers).json()
    # print(f"RESPONSE: {response}")
    error = response.get("error", {})

    # print(error)
    if len(error):
        error_code = error.get("code")

        result = {"status": False, "message": f"Ошибка! {error}"}
    else:
        result = {"status": True, "message": response.get("result", response)}

    return result

async def download_image(session, url, save_path, index):
    filename = os.path.join(save_path, f"{index}.jpg")

    try:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filename, 'wb') as f:
                    f.write(await response.read())
            else:
                print(f"Ошибка загрузки {url}: {response.status}")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")

async def extract_car_images(images: list, save_path: str):
    if not isinstance(images, list):
        return

    os.makedirs(save_path, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, img["uri"], save_path, index) for index, img in enumerate(images) if "uri" in img]
        await asyncio.gather(*tasks)
