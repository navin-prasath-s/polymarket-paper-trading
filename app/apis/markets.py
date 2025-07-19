from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.models.market import Market
from app.schemas.market import Market as MarketSchema

from app.databases.session import get_session

router = APIRouter()

@router.get("/markets",
            response_model=list[MarketSchema],
            status_code=status.HTTP_200_OK)
async def get_tradable_markets():
    with get_session() as db:
        stmt = select(Market).where(Market.is_tradable == True)
        results = db.exec(stmt).all()
        return results


@router.get("/market/{condition_id}",
            response_model=MarketSchema,
            status_code=status.HTTP_200_OK)
async def get_market_by_condition_id(condition_id: str):
    with get_session() as db:
        stmt = select(Market).where(Market.condition_id == condition_id)
        result = db.exec(stmt).first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
        return result