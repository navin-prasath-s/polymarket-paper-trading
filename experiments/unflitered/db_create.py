import sqlite3
from sqlite3 import Connection, Cursor

conn: Connection = sqlite3.connect("unfiltered_market.db")
cursor: Cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS markets (
        condition_id TEXT PRIMARY KEY,
        market_slug TEXT,
        question TEXT,
        enable_order_book INTEGER,
        active INTEGER,
        closed INTEGER,
        archived INTEGER,
        accepting_orders INTEGER,
        tokens_json TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_markets_log (
        timestamp TEXT,
        condition_id TEXT,
        market_slug TEXT,
        question TEXT,
        enable_order_book INTEGER,
        active INTEGER,
        closed INTEGER,
        archived INTEGER,
        accepting_orders INTEGER,
        tokens_json TEXT
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS removed_markets_log (
        timestamp TEXT,
        condition_id TEXT,
        market_slug TEXT,
        question TEXT,
        enable_order_book INTEGER,
        active INTEGER,
        closed INTEGER,
        archived INTEGER,
        accepting_orders INTEGER,
        tokens_json TEXT
    )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS state_changes_log (
    timestamp TEXT,
    condition_id TEXT,
    question TEXT,
    field_changed TEXT,
    old_value INTEGER,
    new_value INTEGER
)
    """)

conn.commit()
conn.close()
print("Database initialized.")