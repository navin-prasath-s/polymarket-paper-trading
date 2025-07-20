from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session

from app.models.market import Market
from app.schemas.market import Market as MarketSchema

from app.core.session import get_session

router = APIRouter(prefix="/markets",
                   tags=["market"])


@router.get("/",
            response_model=list[MarketSchema],
            status_code=status.HTTP_200_OK)
async def get_tradable_markets(
        db: Session = Depends(get_session)
):
    stmt = select(Market).where(Market.is_tradable == True)
    results = db.exec(stmt).all()
    return results


@router.get("/{condition_id}",
            response_model=MarketSchema,
            status_code=status.HTTP_200_OK)
async def get_market_by_condition_id(
        condition_id: str,
    db: Session = Depends(get_session)
):

    stmt = select(Market).where(Market.condition_id == condition_id)
    result = db.exec(stmt).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return result