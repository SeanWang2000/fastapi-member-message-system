import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from routers.auth import auth_router
from routers.message import message_router

load_dotenv()

app = FastAPI()
key = os.environ["SECRET_KEY"]
app.add_middleware(SessionMiddleware, secret_key=key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api")
app.include_router(message_router, prefix="/api")
