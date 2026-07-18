import mysql.connector
from fastapi import APIRouter, Depends, Request
from db import get_db
from schemas import MessageData

message_router = APIRouter()

@message_router.get("/message")
def get_msg(request: Request, db=Depends(get_db)):
    cursor = None
    user_id = request.session.get("user_id")

    try:
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

@message_router.post("/message")
def post_msg(request: Request, body: MessageData, db=Depends(get_db)):
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

    cursor = None

    try:
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
        db.rollback()

        return {
            "success": False,
            "message": "留言發布失敗"
        }

    finally:
        if cursor is not None:
            cursor.close()

@message_router.delete("/message/{message_id}")
def delete_msg(request: Request, message_id: int, db=Depends(get_db)):
    user_id = request.session.get("user_id")

    if user_id is None:
        return {
            "success": False,
            "message": "請先登入"
        }

    cursor = None

    try:
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
        db.rollback()

        return {
            "success": False,
            "message": "留言刪除失敗"
        }
    finally:
        if cursor is not None:
            cursor.close()

