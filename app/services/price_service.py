from datetime import date, datetime, time, timedelta, timezone

from app.clients.deribit import DeribitClient
from app.models.price import Price
from app.repositories.price_repository import PriceRepository


class PriceService:
    ALLOWED_TICKERS = {"btc_usd", "eth_usd"}

    def __init__(
        self,
        repository: PriceRepository,
        deribit_client: DeribitClient,
    ) -> None:
        self.repository = repository
        self.deribit_client = deribit_client

    def validate_ticker(self, ticker: str) -> str:
        ticker = ticker.lower()

        if ticker not in self.ALLOWED_TICKERS:
            raise ValueError(
                f"Unsupported ticker: {ticker}. "
                f"Allowed tickers: {', '.join(sorted(self.ALLOWED_TICKERS))}"
            )

        return ticker

    async def collect_price(self, ticker: str) -> Price:
        ticker = self.validate_ticker(ticker)

        price = await self.deribit_client.get_index_price(ticker)
        timestamp = int(datetime.now(timezone.utc).timestamp())

        return await self.repository.create(
            ticker=ticker,
            price=price,
            timestamp=timestamp,
        )

    async def get_all(self, ticker: str) -> list[Price]:
        ticker = self.validate_ticker(ticker)
        return await self.repository.get_all(ticker)

    async def get_latest(self, ticker: str) -> Price | None:
        ticker = self.validate_ticker(ticker)
        return await self.repository.get_latest(ticker)

    async def get_by_date(
        self,
        ticker: str,
        requested_date: date,
    ) -> list[Price]:
        ticker = self.validate_ticker(ticker)

        start = datetime.combine(
            requested_date,
            time.min,
            tzinfo=timezone.utc,
        )
        end = start + timedelta(days=1)

        return await self.repository.get_by_date(
            ticker=ticker,
            start_timestamp=int(start.timestamp()),
            end_timestamp=int(end.timestamp()),
        )