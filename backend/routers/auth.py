import mysql.connector
from fastapi import APIRouter, Depends, Request

from db import get_db
from password_utils import hash_password, password_hash
from schemas import LoginData, RegisterData
from validators import validate_text
from repositories.user_repository import (
    account_is_available,
    find_user_by_account,
    nickname_is_available,
)

auth_router = APIRouter()


@auth_router.get("/accounts/check")
def check_account(account: str, db=Depends(get_db)):
    error = validate_text(account, "帳號", 6, 20)

    if error is not None:
        return {
            "available": False,
            "message": error
        }

    available = account_is_available(db, account)

    return {
        "available": available,
        "message": "帳號可以使用" if available else "帳號已被使用"
    }


@auth_router.get("/nicknames/check")
def check_nickname(nickname: str, db=Depends(get_db)):
    error = validate_text(nickname, "暱稱", 2, 15)

    if error is not None:
        return {
            "available": False,
            "message": error
        }

    available = nickname_is_available(db, nickname)

    return {
        "available": available,
        "message": "暱稱可以使用" if available else "暱稱已被使用"
    }


@auth_router.get("/session")
def get_session(request: Request):
    return {
        "logged_in": "user_id" in request.session,
        "nickname": request.session.get("nickname"),
    }


@auth_router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {
        "success": True,
        "message": "已登出",
    }


@auth_router.post("/register")
def register(body: RegisterData, db=Depends(get_db)):
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

    if not account_is_available(db, account):
        return {"success": False, "message": "帳號已被使用"}

    if not nickname_is_available(db, nickname):
        return {"success": False, "message": "暱稱已被使用"}

    cursor = None
    try:
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
        db.rollback()
        return {"success": False, "message": "帳號或暱稱已被使用"}
    except mysql.connector.Error as error:
        db.rollback()
        print(error)
        return {"success": False, "message": "資料庫操作失敗"}
    finally:
        if cursor is not None:
            cursor.close()


@auth_router.post("/login")
def login(request: Request, data: LoginData, db=Depends(get_db)):
    user = find_user_by_account(db, data.account)

    if user is None or not password_hash.verify(data.password, user["password_hash"]):
        return {"success": False, "message": "帳號或密碼錯誤"}

    request.session["user_id"] = user["id"]
    request.session["nickname"] = user["nick_name"]
    return {"success": True, "message": "登入成功"}
