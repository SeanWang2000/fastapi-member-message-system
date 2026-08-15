import pytest
from collections.abc import Iterator
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from db import get_db
from main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: MagicMock()

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

def test_get_session_when_not_logged_in(client: TestClient):
    response = client.get("/api/session")

    assert response.status_code == 200
    assert response.json() == {
        "logged_in": False,
        "nickname": None,
    }

@pytest.mark.parametrize("account", ["", "a", "12345", "123 45"])
def test_unavailable_account(client: TestClient, account: str):
    response = client.get(
        "/api/accounts/check",
        params={"account": account}
    )

    assert response.status_code == 200
    assert response.json()["available"] is False