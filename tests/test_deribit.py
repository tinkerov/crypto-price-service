from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.clients.deribit import DeribitClient


@pytest.mark.asyncio
async def test_get_index_price_returns_price():
    client = DeribitClient()

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = AsyncMock(
        return_value={
            "result": {
                "index_price": 65000.5,
            }
        }
    )

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch(
        "app.clients.deribit.aiohttp.ClientSession"
    ) as mock_client_session:
        mock_client_session.return_value.__aenter__.return_value = mock_session

        price = await client.get_index_price("btc_usd")

    assert price == 65000.5
    mock_session.get.assert_called_once()