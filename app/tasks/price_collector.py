import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.clients.deribit import DeribitClient
from app.repositories.price_repository import PriceRepository
from app.services.price_service import PriceService
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.price_collector.collect_prices")
def collect_prices() -> None:
    asyncio.run(_collect_prices())


async def _collect_prices() -> None:
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as session:
            repository = PriceRepository(session)
            client = DeribitClient()
            service = PriceService(repository, client)

            for ticker in ("btc_usd", "eth_usd"):
                await service.collect_price(ticker)
                print(f"Collected price for {ticker}")
    finally:
        await engine.dispose()