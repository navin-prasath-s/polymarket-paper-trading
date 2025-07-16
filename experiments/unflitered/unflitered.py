import time
from datetime import datetime, timezone
import json
import sqlite3
from sqlite3 import Connection, Cursor

from py_clob_client.client import ClobClient

from experiments.minimal_clob_model import MinimalClobModel


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

    return all_markets


def markets_to_market_models(all_markets):
    market_models = []
    for i, d in enumerate(all_markets):
        try:
            market = MinimalClobModel.model_validate(d)
            market_models.append(market)
        except Exception as e:
            print(f"{i}: {e}")

    return market_models


def save_to_db(current_markets):
    conn: Connection = sqlite3.connect("unfiltered_market.db")
    cursor: Cursor = conn.cursor()

    # Fetch existing condition_ids from DB
    cursor.execute("SELECT condition_id FROM markets")
    stored_ids = {row[0] for row in cursor.fetchall()}
    current_ids = {m.condition_id for m in current_markets}

    new_ids = current_ids - stored_ids
    removed_ids = stored_ids - current_ids

    now = datetime.now(timezone.utc).isoformat()

    # Log new markets
    for m in current_markets:
        if m.condition_id in new_ids:
            cursor.execute("""
                           INSERT INTO new_markets_log (timestamp, condition_id, market_slug, question,
                                                        enable_order_book, active, closed, archived,
                                                        accepting_orders, tokens_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, (
                               now, m.condition_id, m.market_slug, m.question,
                               int(m.enable_order_book), int(m.active), int(m.closed),
                               int(m.archived), int(m.accepting_orders),
                               json.dumps([t.model_dump() for t in m.tokens])
                           ))

        # Log removed markets
    for removed_id in removed_ids:
        cursor.execute("SELECT * FROM markets WHERE condition_id = ?", (removed_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                           INSERT INTO removed_markets_log (timestamp, condition_id, market_slug, question,
                                                            enable_order_book, active, closed, archived,
                                                            accepting_orders, tokens_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, (now, *row))


    # Load previous markets for diffing
    cursor.execute(
        "SELECT condition_id, question, enable_order_book, active, closed, archived, accepting_orders FROM markets")
    prev_market_map = {
        row[0]: {
            "question": row[1],
            "enable_order_book": row[2],
            "active": row[3],
            "closed": row[4],
            "archived": row[5],
            "accepting_orders": row[6],
        }
        for row in cursor.fetchall()
    }

    # Track state changes
    for m in current_markets:
        prev = prev_market_map.get(m.condition_id)
        if not prev:
            continue  # new market, already logged elsewhere

        for field in ["enable_order_book", "active", "closed", "archived", "accepting_orders"]:
            old_val = prev[field]
            new_val = int(getattr(m, field))
            if old_val != new_val:
                cursor.execute("""
                               INSERT INTO state_changes_log (timestamp, condition_id, question, field_changed,
                                                              old_value, new_value)
                               VALUES (?, ?, ?, ?, ?, ?)
                               """, (now, m.condition_id, m.question, field, old_val, new_val))

    # Refresh the `markets` table
    cursor.execute("DELETE FROM markets")
    for m in current_markets:
        cursor.execute("""
                       INSERT INTO markets (condition_id, market_slug, question,
                                            enable_order_book, active, closed,
                                            archived, accepting_orders, tokens_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                       """, (
                           m.condition_id, m.market_slug, m.question,
                           int(m.enable_order_book), int(m.active), int(m.closed),
                           int(m.archived), int(m.accepting_orders),
                           json.dumps([t.model_dump() for t in m.tokens])
                       ))



    conn.commit()
    conn.close()


while True:
    try:
        print(f"{datetime.now(timezone.utc).isoformat()} - Fetching market data...")

        all_markets = get_markets()
        market_models = markets_to_market_models(all_markets)

        print(f"Fetched {len(market_models)} total markets")

        unique_market_map = {}
        for m in market_models:
            if m.condition_id not in unique_market_map:
                unique_market_map[m.condition_id] = m

        current_markets = list(unique_market_map.values())

        save_to_db(current_markets)


    except Exception as e:
        print(f"Error during fetch loop: {e}")

    time.sleep(300)