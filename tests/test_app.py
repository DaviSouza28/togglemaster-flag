import importlib
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def app_module(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test:test@localhost:5432/testdb",
    )
    monkeypatch.setenv(
        "AUTH_SERVICE_URL",
        "http://auth-service",
    )

    fake_pool = MagicMock()

    monkeypatch.setattr(
        "psycopg2.pool.SimpleConnectionPool",
        lambda *args, **kwargs: fake_pool,
    )

    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    module.app.config.update(TESTING=True)

    return module


def test_health_returns_ok(app_module):
    client = app_module.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_flags_requires_authorization(app_module):
    client = app_module.app.test_client()

    response = client.get("/flags")

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_invalid_api_key_returns_401(app_module, monkeypatch):
    fake_response = MagicMock()
    fake_response.status_code = 401

    monkeypatch.setattr(
        app_module.requests,
        "get",
        MagicMock(return_value=fake_response),
    )

    client = app_module.app.test_client()

    response = client.get(
        "/flags",
        headers={"Authorization": "Bearer invalid-test-key"},
    )

    assert response.status_code == 401
    assert "error" in response.get_json()
