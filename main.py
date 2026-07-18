import os
import mysql.connector

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from db import get_db_connection
from password_utils import hash_password, password_hash
from schemas import LoginData, MessageData, RegisterData

load_dotenv()

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
key = os.environ["SECRET_KEY"]
app.add_middleware(SessionMiddleware, secret_key=key)

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

def find_user_by_account(account: str):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, nick_name, account, password_hash
            FROM users
            WHERE account = %s
            LIMIT 1
            """,
            (account,)
        )

        return cursor.fetchone()
    finally:
        cursor.close()
        con.close()

@app.get("/api/session")
def get_session(request: Request):
    return {
        "logged_in": "user_id" in request.session,
        "nickname": request.session.get("nickname")
    }

@app.post("/api/logout")
def logout(request: Request):
    request.session.clear()
    return {
        "success": True,
        "message": "已登出"
    }

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

@app.post("/api/login")
def login(request: Request, data: LoginData):
    user = find_user_by_account(data.account)

    if user is None:
        return {
            "success": False,
            "message": "帳號或密碼錯誤"
        }

    if not password_hash.verify(data.password, user["password_hash"]):
        return {
            "success": False,
            "message": "帳號或密碼錯誤"
        }

    request.session["user_id"] = user["id"]
    request.session["nickname"] = user["nick_name"]

    return {
        "success": True,
        "message": "登入成功"
    }

@app.get("/api/message")
def get_msg(request: Request):
    db = None
    cursor = None
    user_id = request.session.get("user_id")

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                m.id,
                u.nick_name,
                m.content,
                m.create_time,
                (m.user_id = %s) AS can_delete
            FROM message AS m
            JOIN users AS u ON m.user_id = u.id
            ORDER BY m.create_time DESC
        """, (user_id,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

@app.delete("/api/message/{message_id}")
def delete_msg(request: Request, message_id: int):
    user_id = request.session.get("user_id")

    if user_id is None:
        return {
            "success": False,
            "message": "請先登入"
        }

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM message WHERE id = %s AND user_id = %s",
            (message_id, user_id)
        )

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": "留言不存在或無權限刪除"
            }

        db.commit()
        return {
            "success": True,
            "message": "留言刪除成功"
        }
    except mysql.connector.Error:
        if db is not None:
            db.rollback()

        return {
            "success": False,
            "message": "留言刪除失敗"
        }
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

@app.post("/api/message")
def post_msg(request: Request, body: MessageData):
    user_id = request.session.get("user_id")

    if user_id is None:
        return {
            "success": False,
            "message": "請先登入"
        }

    content = body.content.strip()

    if not content:
        return {
            "success": False,
            "message": "留言內容不可為空白"
        }

    if len(content) > 500:
        return {
            "success": False,
            "message": "留言內容不可超過 500 個字元"
        }

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO message (user_id, content)
            VALUES (%s, %s)
        """, (user_id, content))

        db.commit()

        return {
            "success": True,
            "message": "留言發布成功"
        }

    except mysql.connector.Error:
        if db is not None:
            db.rollback()

        return {
            "success": False,
            "message": "留言發布失敗"
        }

    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()

app.mount("/", StaticFiles(directory="public", html=True))
