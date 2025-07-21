import os

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.tracked_market import TrackedMarketCreate
from app.models.market import Market
from app.core.session import get_async_session

load_dotenv()
API_KEY = os.getenv("INTERNAL_API_KEY")


router = APIRouter(prefix="/market_events",
                   tags=["market_events"])


@router.post("/add",
             status_code=status.HTTP_201_CREATED,
             description="Creates a new market.")
async def add_tracked_market(
    markets: list[TrackedMarketCreate],
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_async_session)
    ) -> dict:

    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not markets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No markets provided")

    created = 0
    for market in markets:
        new_market = Market(
            condition_id=market.condition_id,
            market_slug=market.market_slug,
            is_tradable=True
        )
        try:
            db.add(new_market)
            await db.commit()
            await db.refresh(new_market)
            created += 1
        except IntegrityError:
            await db.rollback()
            print(f"Market with condition_id {market.condition_id} already exists.")
        except Exception as e:
            await db.rollback()
            print(f"Failed to add market {market.condition_id}: {str(e)}")

    return {"message": f"{created} market(s) added"}


@router.put("/remove",
             status_code=status.HTTP_200_OK,
             description="Marks a market as untradable.")
async def remove_tracked_market(
    condition_ids: list[str],
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_async_session)
    ) -> dict:

    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not condition_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No condition IDs provided")

    stmt = select(Market).where(Market.condition_id.in_(condition_ids))
    result = await db.execute(stmt)
    markets = result.scalars().all()

    updated = 0
    for market in markets:
        market.is_tradable = False
        db.add(market)
        updated += 1

    await db.commit()

    return {"message": f"{updated} market(s) marked as untradable"}

