import pytest
from collections.abc import Iterator
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client

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