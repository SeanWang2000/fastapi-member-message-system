import os
from collections.abc import Generator

import mysql.connector
from mysql.connector.connection import MySQLConnection


def get_db_connection() -> MySQLConnection:
    return mysql.connector.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
    )


def get_db() -> Generator[MySQLConnection]:
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()
