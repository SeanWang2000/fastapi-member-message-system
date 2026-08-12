from unittest.mock import MagicMock

from repositories.user_repository import (
    account_is_available,
    find_user_by_account,
    nickname_is_available,
)


def test_account_is_available():
    db = MagicMock()
    cursor = db.cursor.return_value
    cursor.fetchone.return_value = None

    result = account_is_available(db, "alice")

    assert result is True
    cursor.execute.assert_called_once_with(
        "SELECT 1 FROM users WHERE account = %s LIMIT 1",
        ("alice",),
    )
    cursor.close.assert_called_once()


def test_account_is_not_available():
    db = MagicMock()
    cursor = db.cursor.return_value
    cursor.fetchone.return_value = (1,)

    result = account_is_available(db, "alice")

    assert result is False
    cursor.close.assert_called_once()


# def test_nickname_is_available_when_nickname_does_not_exist():
#     db = MagicMock()
#     cursor = db.cursor.return_value
#     cursor.fetchone.return_value = None

#     result = nickname_is_available(db, "Alice")

#     assert result is True
#     cursor.execute.assert_called_once_with(
#         "SELECT 1 FROM users WHERE nick_name = %s LIMIT 1",
#         ("Alice",),
#     )
#     cursor.close.assert_called_once()


# def test_find_user_by_account_returns_user():
#     db = MagicMock()
#     cursor = db.cursor.return_value
#     user = {
#         "id": 1,
#         "nick_name": "Alice",
#         "account": "alice",
#         "password_hash": "hashed-password",
#     }
#     cursor.fetchone.return_value = user

#     result = find_user_by_account(db, "alice")

#     assert result == user
#     db.cursor.assert_called_once_with(dictionary=True)
#     cursor.execute.assert_called_once()
#     assert cursor.execute.call_args.args[1] == ("alice",)
#     cursor.close.assert_called_once()


# def test_find_user_by_account_returns_none_when_user_does_not_exist():
#     db = MagicMock()
#     cursor = db.cursor.return_value
#     cursor.fetchone.return_value = None

#     result = find_user_by_account(db, "unknown")

#     assert result is None
#     cursor.close.assert_called_once()
