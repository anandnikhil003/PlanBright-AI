import os
from typing import Optional
from dotenv import load_dotenv
import requests
from fastapi import status, Query, WebSocket, WebSocketException, Header
from security.dev_tokens import verify_dev_token

# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


load_dotenv()

VALID_URL = os.getenv("VALID_URL")
AUTH_URL = os.getenv("AUTH_URL")
PROFILE_URL = os.getenv("PROFILE_URL")
AUTH_MODE = os.getenv("AUTH_MODE", "external").strip().lower()


def verify_token(token: str) -> Optional[str]:
    if AUTH_MODE == "development":
        return verify_dev_token(token)

    url = VALID_URL
    headers = {"token": token}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("status") == "SUCCESS":
                user_id = json_data.get("data")
                return user_id
            else:
                print("Token validation failed.")
        else:
            print("Error:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)
        return None


def user_name_token(token: str = Header(...)) -> Optional[str]:
    if AUTH_MODE == "development":
        return "Local Developer" if verify_dev_token(token) else None

    url = PROFILE_URL
    print(url)
    print(token)
    headers = {"token": token}
    try:
        response = requests.get(url, headers=headers)
        print(response)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("status") == "SUCCESS":
                personal_data = json_data.get("data")
                first_name = personal_data.get("firstName")
                last_name = personal_data.get("lastName")
                full_name = f"{first_name} {last_name}"
                return full_name
            else:
                print("Token validation failed.")
        else:
            print("Error:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)
        return None


async def get_or_verify_token(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    url = VALID_URL
    headers = {"token": token}
    # Handle case where token is None
    if token is None:
        return {"user_id": None, "token": None}
    if AUTH_MODE == "development":
        user_id = verify_dev_token(token)
        if user_id:
            return {"user_id": user_id, "token": token}
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid or expired development token",
        )
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("status") == "SUCCESS":
                user_id = json_data.get("data")
                return {"user_id": user_id, "token": token}
            else:
                print("Token validation failed.")
        else:
            print("Error:", response.status_code)
    except Exception:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Could not validate credentials",
        )


async def update_activity(token: str):
    if AUTH_MODE == "development":
        return
    url = AUTH_URL
    headers = {"token": token}
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("status") == "SUCCESS":
                print("User activity updated successfully")
            else:
                print("User activity updated unsuccessfully")
        else:
            print("Error:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)
