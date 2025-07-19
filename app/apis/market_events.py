import os

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, status

from app.schemas.tracked_market import TrackedMarketSchema

load_dotenv()
router = APIRouter()

API_KEY = db_user = os.getenv("INTERNAL_API_KEY")


@router.post("/market/new", status_code=status.HTTP_201_CREATED)
async def add_tracked_market(
    markets: list[TrackedMarketSchema],
    x_api_key: str = Header(...)
    ):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    for market in markets:
        print(f"New market: {market.condition_id}")

    return {"message": f"{len(markets)} market(s) added"}


@router.post("/market/removed", status_code=status.HTTP_200_OK)
async def remove_tracked_market(
    markets: list[TrackedMarketSchema],
    x_api_key: str = Header(...)
    ):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    for market in markets:
        print(f"Removed market: {market.condition_id}")

    return {"message": f"{len(markets)} market(s) removed"}

