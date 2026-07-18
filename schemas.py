from pydantic import BaseModel


class RegisterData(BaseModel):
    account: str
    nickname: str
    password: str


class LoginData(BaseModel):
    account: str
    password: str


class MessageData(BaseModel):
    content: str
