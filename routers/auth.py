import mysql.connector

from fastapi import APIRouter, Request

from db import get_db_connection
from password_utils import hash_password, password_hash
from schemas import LoginData, RegisterData
from validators import validate_text


router = APIRouter()


def account_is_available(account: str) -> bool:
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE account = %s LIMIT 1",
            (account,),
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
            (nickname,),
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
            (account,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        con.close()


@router.get("/session")
def get_session(request: Request):
    return {
        "logged_in": "user_id" in request.session,
        "nickname": request.session.get("nickname"),
    }


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {
        "success": True,
        "message": "已登出",
    }


@router.post("/register")
def register(body: RegisterData):
    account = body.account
    nickname = body.nickname
    password = body.password

    account_error = validate_text(account, "帳號", 6, 20)
    if account_error is not None:
        return {"success": False, "message": account_error}

    nickname_error = validate_text(nickname, "暱稱", 2, 15)
    if nickname_error is not None:
        return {"success": False, "message": nickname_error}

    password_error = validate_text(password, "密碼", 6, 20)
    if password_error is not None:
        return {"success": False, "message": password_error}

    if not account_is_available(account):
        return {"success": False, "message": "帳號已被使用"}

    if not nickname_is_available(nickname):
        return {"success": False, "message": "暱稱已被使用"}

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
            (account, nickname, hash_password(password)),
        )
        db.commit()
        return {"success": True, "message": "註冊成功"}
    except mysql.connector.IntegrityError:
        if db is not None:
            db.rollback()
        return {"success": False, "message": "帳號或暱稱已被使用"}
    except mysql.connector.Error as error:
        if db is not None:
            db.rollback()
        print(error)
        return {"success": False, "message": "資料庫操作失敗"}
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


@router.post("/login")
def login(request: Request, data: LoginData):
    user = find_user_by_account(data.account)
    invalid_credentials = {"success": False, "message": "帳號或密碼錯誤"}

    if user is None or not password_hash.verify(data.password, user["password_hash"]):
        return invalid_credentials

    request.session["user_id"] = user["id"]
    request.session["nickname"] = user["nick_name"]
    return {"success": True, "message": "登入成功"}
