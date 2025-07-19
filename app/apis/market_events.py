import os

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.schemas.tracked_market import TrackedMarketSchema
from app.models.market import Market
from app.databases.session import get_session

load_dotenv()
router = APIRouter()

API_KEY = os.getenv("INTERNAL_API_KEY")


@router.post("/market/add",
             status_code=status.HTTP_201_CREATED)
async def add_tracked_market(
    markets: list[TrackedMarketSchema],
    x_api_key: str = Header(...)
    ):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    created = 0
    with get_session() as db:
        for market in markets:
            new_market = Market(
                condition_id=market.condition_id,
                market_slug=market.market_slug,
                is_tradable=True
            )
            try:
                db.add(new_market)
                db.commit()
                created += 1
            except IntegrityError:
                db.rollback()
                print(f"Market with condition_id {market.condition_id} already exists.")

    return {"message": f"{created} market(s) added"}


@router.post("/market/remove",
             status_code=status.HTTP_200_OK)
async def remove_tracked_market(
    markets: list[TrackedMarketSchema],
    x_api_key: str = Header(...)
    ):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    updated  = 0
    with get_session() as db:
        for market in markets:
            stmt = select(Market).where(Market.condition_id == market.condition_id)  # type: ignore
            result = db.execute(stmt).scalar_one_or_none()

            if result:
                result.is_tradable = False
                db.add(result)
                db.commit()
                updated += 1
            else:
                print(f"Market not found: {market.condition_id}")

    return {"message": f"{updated} market(s) marked as untradable"}

