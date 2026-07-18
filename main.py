import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from routers.auth import auth_router, nickname_is_available, account_is_available
from routers.message import message_router
from validators import validate_text

load_dotenv()

app = FastAPI()
key = os.environ["SECRET_KEY"]
app.add_middleware(SessionMiddleware, secret_key=key)
app.include_router(auth_router, prefix="/api")
app.include_router(message_router, prefix="/api")


@app.get("/api/accounts/check")
def check_account(account: str):
    error = validate_text(account, "帳號", 6, 20)

    if error is not None:
        return {
            "available": False,
            "message": error
        }

    available = account_is_available(account)

    return {
        "available": available,
        "message": "帳號可以使用" if available else "帳號已被使用"
    }


@app.get("/api/nicknames/check")
def check_nickname(nickname: str):
    error = validate_text(nickname, "暱稱", 2, 15)

    if error is not None:
        return {
            "available": False,
            "message": error
        }

    available = nickname_is_available(nickname)

    return {
        "available": available,
        "message": "暱稱可以使用" if available else "暱稱已被使用"
    }


app.mount("/", StaticFiles(directory="public", html=True))
