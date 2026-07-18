from db import get_db_connection


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
