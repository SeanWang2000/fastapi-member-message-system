import os
import mysql.connector

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from password_utils import hash_password

load_dotenv()

# 目前為學習與小型專案，採用每次操作建立並關閉連線的方式。
def get_db_connection():
    return mysql.connector.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME")
    )

class RegisterData(BaseModel):
    account: str
    nickname: str
    password: str

def validate_text(
    value: str,
    field_name: str,
    min_length: int,
    max_length: int
) -> str | None:

    if any(char.isspace() for char in value):
        return f"{field_name}不可包含空白"

    if not min_length <= len(value) <= max_length:
        return f"{field_name}長度必須為 {min_length}～{max_length} 個字元"

    return None

app = FastAPI()

def account_is_available(account: str) -> bool:
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE account = %s LIMIT 1",
            (account,)
        )
        return cursor.fetchone() is None
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


def nickname_is_available(nickname: str) -> bool:
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE nick_name = %s LIMIT 1",
            (nickname,)
        )
        return cursor.fetchone() is None
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

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

@app.post("/api/register")
def register(body: RegisterData):
    account = body.account
    nickname = body.nickname
    password = body.password

    account_error = validate_text(account, "帳號", 6, 20)

    if account_error is not None:
        return {
            "success": False,
            "message": account_error
        }

    nickname_error = validate_text(nickname, "暱稱", 2, 15)

    if nickname_error is not None:
        return {
            "success": False,
            "message": nickname_error
        }

    password_error = validate_text(password, "密碼", 6, 20)

    if password_error is not None:
        return {
            "success": False,
            "message": password_error
        }

    if not account_is_available(account):
        return {
            "success": False,
            "message": "帳號已被使用"
        }

    if not nickname_is_available(nickname):
        return {
            "success": False,
            "message": "暱稱已被使用"
        }

    hashed_password = hash_password(password)
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO users (account, nick_name, password_hash)
            VALUES (%s, %s, %s)
            """,
            (account, nickname, hashed_password)
        )

        db.commit()

        return {
            "success": True,
            "message": "註冊成功"
        }

    except mysql.connector.IntegrityError:
        if db is not None:
            db.rollback()

        return {
            "success": False,
            "message": "帳號或暱稱已被使用"
        }

    except mysql.connector.Error as error:
        if db is not None:
            db.rollback()

        print(error)

        return {
            "success": False,
            "message": "資料庫操作失敗"
        }

    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()









@app.get("/api/message")
def get_msg():
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM message")
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


app.mount("/", StaticFiles(directory="public", html=True))
