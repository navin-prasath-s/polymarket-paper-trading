import argparse
from datetime import datetime, timezone, timedelta

from sqlmodel import select

from app.models.market_change_log import MarketChangeLog
from app.databases.session import get_session

def create_dummy_logs():
    now = datetime.now(timezone.utc)
    return [
        MarketChangeLog(condition_id="cond_001", change_type="added", timestamp=now),
        MarketChangeLog(condition_id="cond_002", change_type="deleted", timestamp=now - timedelta(minutes=1)),
        MarketChangeLog(condition_id="cond_003", change_type="added", timestamp=now - timedelta(minutes=2)),
    ]


def insert_logs():
    logs = create_dummy_logs()
    with get_session() as session:
        session.add_all(logs)
        session.commit()
        print("Inserted dummy logs.")


def fetch_logs():
    with get_session() as session:
        logs = session.exec(select(MarketChangeLog)).all()
        for log in logs:
            print(log)


def update_log():
    with get_session() as session:
        stmt = select(MarketChangeLog).where(MarketChangeLog.condition_id == "cond_001")
        log = session.exec(stmt).first()
        if log:
            log.change_type = "deleted"
            session.add(log)
            session.commit()
            print("Updated log for cond_001.")
        else:
            print("No log found for cond_001.")

def delete_logs():
    dummy_logs = create_dummy_logs()
    with get_session() as session:
        for log in dummy_logs:
            db_log = session.exec(
                select(MarketChangeLog).where(MarketChangeLog.condition_id == log.condition_id)
            ).first()
            if db_log:
                session.delete(db_log)
        session.commit()
        print("Deleted dummy logs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--insert", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--delete", action="store_true")

    args = parser.parse_args()

    if args.insert:
        insert_logs()
    if args.fetch:
        fetch_logs()
    if args.update:
        update_log()
    if args.delete:
        delete_logs()

