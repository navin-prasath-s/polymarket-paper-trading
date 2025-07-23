import asyncio
import os
import httpx

from dotenv import load_dotenv
from sqlmodel import select
from py_clob_client.client import ClobClient

from app.models.tracked_market import TrackedMarket, TrackedMarketCreate
from app.models.market_change_log import MarketChangeLog, MarketChangeType
from app.core.session import get_async_manager, engine

load_dotenv()
API_KEY = os.getenv("INTERNAL_API_KEY")
URL_BASE = os.getenv("API_BASE_URL")
HEADERS = {"x-api-key": API_KEY}



def get_markets():
    host: str = "https://clob.polymarket.com"
    open_client: ClobClient = ClobClient(host=host)
    start_cursor = "MA=="
    end_cursor = "LTE="

    all_markets = []
    next_cursor = start_cursor
    while next_cursor != end_cursor:
        response = open_client.get_markets(next_cursor=next_cursor)

        markets = response.get("data", [])
        all_markets.extend(markets)

        next_cursor = response.get("next_cursor")

    filtered = [
        m for m in all_markets
        if m.get("enable_order_book") and m.get("accepting_orders")
    ]

    return filtered

async def handle_new_markets(db, clob_markets, newly_added_ids, client: httpx.AsyncClient):
    to_post = []
    for market in clob_markets:
        if market["condition_id"] in newly_added_ids:

            try:
                schema_obj = TrackedMarketCreate(**market)
                model_obj = TrackedMarket(**schema_obj.model_dump())
                db.add(model_obj)

                log = MarketChangeLog(
                    condition_id=model_obj.condition_id,
                    change_type=MarketChangeType.ADDED
                )
                db.add(log)

                await db.commit()
                await db.refresh(model_obj)
                to_post.append(schema_obj)

            except Exception as e:
                await db.rollback()
                print(f"Insert failed for {market['condition_id']}: {e}")

    if to_post:
        print(f"Posting {len(to_post)} new markets")
        try:
            response = await client.post(f"{URL_BASE}/market/",
                                  json=[m.model_dump() for m in to_post],
                                  headers=HEADERS,
                                  timeout=90)
            print("RESPONSE STATUS:", response.status_code)
            print("RESPONSE BODY:", response.text)
            response.raise_for_status()
        except Exception as e:
            print(f"POST /market_events/add failed: {e}")



async def handle_removed_markets(db, db_markets, removed_ids, client: httpx.AsyncClient):
    to_post = []
    for m in db_markets:
        if m.condition_id in removed_ids:
            try:
                to_post.append(TrackedMarketCreate.model_validate(m))
                await db.delete(m)

                log = MarketChangeLog(
                    condition_id=m.condition_id,
                    change_type=MarketChangeType.DELETED
                )
                db.add(log)

                await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"Delete failed for {m.condition_id}: {e}")

    if to_post:
        print(f"Removing {len(to_post)} old markets")
        try:
            response = await client.patch(f"{URL_BASE}/market/untradable/",
                                 json=[m.model_dump() for m in to_post],
                                 headers=HEADERS)
            print("RESPONSE STATUS:", response.status_code)
            print("RESPONSE BODY:", response.text)
            response.raise_for_status()
        except Exception as e:
            print(f"POST /market_events/remove failed: {e}")


async def run_diff_check():
    async with get_async_manager() as db:
        db_result = await db.execute(select(TrackedMarket))
        db_markets = db_result.scalars().all()
        db_condition_ids = {m.condition_id for m in db_markets }


        clob_markets = get_markets()
        clob_condition_ids = {m["condition_id"] for m in clob_markets}

        newly_added = clob_condition_ids - db_condition_ids
        removed = db_condition_ids - clob_condition_ids

        async with httpx.AsyncClient(timeout=90) as client:
            await handle_new_markets(db, clob_markets, newly_added, client)
            await handle_removed_markets(db, db_markets, removed, client)

    await engine.dispose()



if __name__ == "__main__":
    asyncio.run(run_diff_check())



