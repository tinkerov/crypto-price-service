from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.price import PriceResponse
from app.repositories.price_repository import PriceRepository
from app.services.price_service import PriceService
from app.clients.deribit import DeribitClient

router = APIRouter(prefix="/prices", tags=["Prices"])


def get_price_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PriceService:
    repository = PriceRepository(session)
    client = DeribitClient()
    return PriceService(repository, client)


@router.get("", response_model=list[PriceResponse])
async def get_all_prices(
    ticker: Annotated[str, Query(description="Например, btc_usd или eth_usd")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PriceResponse]:
    try:
        return await service.get_all(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(
    ticker: Annotated[str, Query(description="Например, btc_usd или eth_usd")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PriceResponse:
    try:
        record = await service.get_latest(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if record is None:
        raise HTTPException(status_code=404, detail="Price not found")

    return record


@router.get("/by-date", response_model=list[PriceResponse])
async def get_prices_by_date(
    ticker: Annotated[str, Query(description="Например, btc_usd или eth_usd")],
    requested_date: Annotated[date, Query(alias="date")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PriceResponse]:
    try:
        return await service.get_by_date(ticker, requested_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc