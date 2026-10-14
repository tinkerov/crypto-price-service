from unittest.mock import AsyncMock

import pytest

from app.services.price_service import PriceService


@pytest.fixture
def service():
    repository = AsyncMock()
    deribit_client = AsyncMock()

    return PriceService(
        repository=repository,
        deribit_client=deribit_client,
    )


def test_validate_ticker_accepts_supported_tickers(service):
    assert service.validate_ticker("btc_usd") == "btc_usd"
    assert service.validate_ticker("eth_usd") == "eth_usd"
    assert service.validate_ticker("BTC_USD") == "btc_usd"


def test_validate_ticker_rejects_unsupported_ticker(service):
    with pytest.raises(ValueError, match="Unsupported ticker"):
        service.validate_ticker("doge_usd")


@pytest.mark.asyncio
async def test_collect_price_saves_price(service):
    service.deribit_client.get_index_price.return_value = 65000.5
    service.repository.create.return_value = "saved_record"

    result = await service.collect_price("btc_usd")

    assert result == "saved_record"

    service.deribit_client.get_index_price.assert_awaited_once_with(
        "btc_usd"
    )

    service.repository.create.assert_awaited_once()

    kwargs = service.repository.create.call_args.kwargs
    assert kwargs["ticker"] == "btc_usd"
    assert kwargs["price"] == 65000.5
    assert isinstance(kwargs["timestamp"], int)