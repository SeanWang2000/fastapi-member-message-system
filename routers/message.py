import mysql.connector
from fastapi import APIRouter, Depends, Request
from db import get_db
from repositories import message_repository
from schemas import MessageData

message_router = APIRouter()

@message_router.get("/message")
def get_msg(request: Request, db=Depends(get_db)):
    user_id = request.session.get("user_id")
    return message_repository.find_messages(db, user_id)

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

    try:
        message_repository.create_message(db, user_id, content)
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

@message_router.delete("/message/{message_id}")
def delete_msg(request: Request, message_id: int, db=Depends(get_db)):
    user_id = request.session.get("user_id")

    if user_id is None:
        return {
            "success": False,
            "message": "請先登入"
        }

    try:
        if not message_repository.delete_message(db, message_id, user_id):
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

