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

def enable_order_book_true_and_accepting_orders_true(markets):
    enable_order_book_true_and_accepting_orders_true = []
    for m in markets:
        if m.enable_order_book and m.accepting_orders:
            enable_order_book_true_and_accepting_orders_true.append(m)
    return enable_order_book_true_and_accepting_orders_true


def save_to_db(current_markets):
    conn: Connection = sqlite3.connect("enable_order_book_true.db")
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
        filtered_markets = enable_order_book_true_and_accepting_orders_true(market_models)

        print(f"Fetched {len(filtered_markets)} active & accepting markets")

        save_to_db(filtered_markets)

        # with open(f"snapshots/markets_order_book_{datetime.now(timezone.utc).isoformat()}.json", "w") as f:
        #     json.dump([m.model_dump() for m in filtered_markets], f, indent=2)

    except Exception as e:
        print(f"Error during fetch loop: {e}")

    time.sleep(300)