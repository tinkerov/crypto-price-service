from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import Price


class PriceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        ticker: str,
        price: float,
        timestamp: int,
    ) -> Price:
        record = Price(
            ticker=ticker,
            price=price,
            timestamp=timestamp,
        )

        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)

        return record

    async def get_all(self, ticker: str) -> list[Price]:
        result = await self.session.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_latest(self, ticker: str) -> Price | None:
        result = await self.session.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_date(
        self,
        ticker: str,
        start_timestamp: int,
        end_timestamp: int,
    ) -> list[Price]:
        result = await self.session.execute(
            select(Price)
            .where(
                Price.ticker == ticker,
                Price.timestamp >= start_timestamp,
                Price.timestamp < end_timestamp,
            )
            .order_by(Price.timestamp.desc())
        )
        return list(result.scalars().all())