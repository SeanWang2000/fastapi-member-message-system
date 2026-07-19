from pytest import MonkeyPatch
from unittest.mock import MagicMock, patch

from db import get_db, get_db_connection

def test_get_db_connection_uses_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("DB_USER", "test-user")
    monkeypatch.setenv("DB_PASSWORD", "test-password")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_NAME", "test-db")

    with patch("db.mysql.connector.connect") as connect:
        get_db_connection()

    connect.assert_called_once_with(
        user="test-user",
        password="test-password",
        host="localhost",
        database="test-db",
    )


def test_get_db_yields_and_closes_connections():
    connection = MagicMock()

    with patch("db.get_db_connection", return_value=connection):
        generator = get_db()

        assert next(generator) is connection

        try:
            next(generator)
        except StopIteration:
            pass

    connection.close.assert_called_once()
