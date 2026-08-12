from mysql.connector.connection import MySQLConnection


def find_messages(db: MySQLConnection, user_id: int | None) -> list[dict]:
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                m.id,
                u.nick_name,
                m.content,
                m.create_time,
                (m.user_id = %s) AS can_delete
            FROM message AS m
            JOIN users AS u ON m.user_id = u.id
            ORDER BY m.create_time DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def create_message(db: MySQLConnection, user_id: int, content: str) -> None:
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO message (user_id, content)
            VALUES (%s, %s)
            """,
            (user_id, content),
        )
    finally:
        cursor.close()


def delete_message(db: MySQLConnection, message_id: int, user_id: int) -> bool:
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM message WHERE id = %s AND user_id = %s",
            (message_id, user_id),
        )
        return cursor.rowcount > 0
    finally:
        cursor.close()
