import time
from datetime import datetime, timezone
import json

from sqlmodel import select
from py_clob_client.client import ClobClient

from app.schemas.tracked_market import TrackedMarketSchema
from app.models.tracked_market import TrackedMarket
from app.databases.session import get_session



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



def run_diff_check():
    with get_session() as db:
        db_result = db.execute(select(TrackedMarket))
        db_markets = db_result.scalars().all()
        db_condition_ids = {m.condition_id for m in db_markets }


        clob_markets = get_markets()
        clob_condition_ids = {m["condition_id"] for m in clob_markets}

        newly_added = clob_condition_ids - db_condition_ids
        removed = db_condition_ids - clob_condition_ids

        print(f"New markets: {newly_added}")
        print(f"Removed markets: {removed}")


        for market in clob_markets:
            if market["condition_id"] in newly_added:
                try:
                    schema_obj = TrackedMarketSchema(**market)
                    model_obj = TrackedMarket(**schema_obj.model_dump())
                    db.add(model_obj)
                    db.commit()
                    db.refresh(model_obj)

                    print(f"Inserted new market: {model_obj.condition_id}")

                except Exception as e:
                    print(f"Failed to insert or POST for {market['condition_id']}: {e}")

        for m in db_markets:
            if m.condition_id in removed:
                print(f"Market missing from CLOB now: {m.condition_id}")
                try:
                    db.delete(m)
                    db.commit()
                    print(f"🗑Removed stale market from DB: {m.condition_id}")
                except Exception as e:
                    print(f"Failed to delete stale market: {e}")



if __name__ == "__main__":
    run_diff_check()