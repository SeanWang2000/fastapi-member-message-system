import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from routers.auth import auth_router
from routers.message import message_router

load_dotenv()

app = FastAPI()
key = os.environ["SECRET_KEY"]
app.add_middleware(SessionMiddleware, secret_key=key)
app.include_router(auth_router, prefix="/api")
app.include_router(message_router, prefix="/api")

app.mount("/", StaticFiles(directory="public", html=True))
