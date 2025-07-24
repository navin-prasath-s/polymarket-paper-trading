import os

from dotenv import load_dotenv
from fastapi import APIRouter, status, Depends, HTTPException, Header
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.session import get_async_session
from app.models.market import Market, MarketRead, MarketCreate

load_dotenv()
API_KEY = os.getenv("INTERNAL_API_KEY")



router = APIRouter(prefix="/market",
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
            detail=f"Failed to fetch markets {e}"
        )


@router.get("/{condition_id}",
            response_model=MarketRead,
            status_code=status.HTTP_200_OK,
            description="Retrieve a market by its condition ID.")
async def get_tradable_market_by_condition_id(
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve market {e}"
        )


@router.post("/",

             status_code=status.HTTP_201_CREATED,
             description="Creates one or more new tradable market.")
async def add_tradable_market(
    markets: list[MarketCreate],
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_async_session)
    ) -> dict:

    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized")
    if not markets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No markets provided")

    created = 0
    errors = []
    for market in markets:
        new_market = Market(
            condition_id=market.condition_id,
            market_slug=market.market_slug,
        )
        try:
            db.add(new_market)
            await db.commit()
            await db.refresh(new_market)
            created += 1
        except IntegrityError:
            await db.rollback()
            errors.append(f"Market with condition_id {market.condition_id} already exists.")
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add market {market.condition_id}: {str(e)}"
            )

    if errors and created == 0:
        raise HTTPException(status_code=400, detail=errors)
    elif errors:
        return {
            "message": f"{created} market(s) added, {len(errors)} duplicate(s) skipped",
            "errors": errors
        }
    else:
        return {"message": f"{created} market(s) added"}



@router.patch("/untradable/",
             status_code=status.HTTP_200_OK,
             description="Marks one or more market as untradable.")
async def mark_markets_untradable(
    condition_ids: list[str],
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_async_session)
    ) -> dict:

    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not condition_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No condition IDs provided")
    try:
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

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown error: {str(e)}"
        )

