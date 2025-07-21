from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.session import get_async_session
from app.models.market import Market, MarketRead


router = APIRouter(prefix="/markets",
                   tags=["market"])


@router.get("/",
            response_model=list[MarketRead],
            status_code=status.HTTP_200_OK,
            description="Retrieve all tradable markets.")
async def get_tradable_markets(
        db: AsyncSession = Depends(get_async_session)
) -> list[MarketRead]:
    try:
        stmt = select(Market).where(Market.is_tradable == True)
        results = await db.execute(stmt)
        return results.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch markets"
        ) from e


@router.get("/{condition_id}",
            response_model=MarketRead,
            status_code=status.HTTP_200_OK,
            description="Retrieve a market by its condition ID.")
async def get_market_by_condition_id(
        condition_id: str,
        db: AsyncSession = Depends(get_async_session)
) -> MarketRead:
    try:
        stmt = select(Market).where(Market.condition_id == condition_id)
        result = await db.execute(stmt)
        market = result.scalar_one_or_none()
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market not found"
            )
        return market
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market"
        ) from e