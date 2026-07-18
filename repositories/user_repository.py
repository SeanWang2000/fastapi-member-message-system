from mysql.connector.connection import MySQLConnection

def account_is_available(db: MySQLConnection, account: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM users WHERE account = %s LIMIT 1",
            (account,),
        )
        return cursor.fetchone() is None
    finally:
        cursor.close()


def nickname_is_available(db: MySQLConnection, nickname: str) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM users WHERE nick_name = %s LIMIT 1",
            (nickname,),
        )
        return cursor.fetchone() is None
    finally:
        cursor.close()


def find_user_by_account(db: MySQLConnection, account: str) -> dict | None:
    cursor = db.cursor(dictionary=True)
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
