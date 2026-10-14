from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_price_service
from app.main import app


@pytest.fixture
def client():
    service = MagicMock()

    record = MagicMock()
    record.id = 1
    record.ticker = "btc_usd"
    record.price = 65000.5
    record.timestamp = 1791914400

    service.get_all = AsyncMock(return_value=[record])
    service.get_latest = AsyncMock(return_value=record)
    service.get_by_date = AsyncMock(return_value=[record])

    app.dependency_overrides[get_price_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_all_prices(client):
    response = client.get("/prices?ticker=btc_usd")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ticker"] == "btc_usd"


def test_get_latest_price(client):
    response = client.get("/prices/latest?ticker=btc_usd")

    assert response.status_code == 200
    assert response.json()["price"] == 65000.5


def test_get_prices_by_date(client):
    response = client.get(
        "/prices/by-date",
        params={
            "ticker": "btc_usd",
            "date": date.today().isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json()[0]["ticker"] == "btc_usd"


def test_latest_price_returns_404_when_not_found(client):
    service = app.dependency_overrides[get_price_service]()
    service.get_latest.return_value = None

    response = client.get("/prices/latest?ticker=btc_usd")

    assert response.status_code == 404


def test_prices_require_ticker(client):
    response = client.get("/prices")

    assert response.status_code == 422