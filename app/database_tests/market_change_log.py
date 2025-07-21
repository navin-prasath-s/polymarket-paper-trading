import argparse
from datetime import datetime, timezone, timedelta

from sqlmodel import select

from app.models.market_change_log import MarketChangeLog
from app.core.session import get_async_session

def create_dummy_logs():
    now = datetime.now(timezone.utc)
    return [
        MarketChangeLog(condition_id="cond_001", change_type="added", timestamp=now),
        MarketChangeLog(condition_id="cond_002", change_type="deleted", timestamp=now - timedelta(minutes=1)),
        MarketChangeLog(condition_id="cond_003", change_type="added", timestamp=now - timedelta(minutes=2)),
    ]


async def insert_logs():
    logs = create_dummy_logs()
    async with get_async_session() as session:
        session.add_all(logs)
        await session.commit()
        print("Inserted dummy logs.")


async def fetch_logs():
    async with get_async_session() as session:
        result = await session.execute(select(MarketChangeLog))
        logs = result.scalars().all()
        for log in logs:
            print(log)


async def update_log():
    async with get_async_session() as session:
        stmt = select(MarketChangeLog).where(MarketChangeLog.condition_id == "cond_001")
        result = await session.execute(stmt)
        log = result.scalars().first()
        if log:
            log.change_type = "deleted"
            session.add(log)
            await session.commit()
            print("Updated log for cond_001.")
        else:
            print("No log found for cond_001.")

async def delete_logs():
    dummy_logs = create_dummy_logs()
    async with get_async_session() as session:
        for log in dummy_logs:
            stmt = select(MarketChangeLog).where(MarketChangeLog.condition_id == log.condition_id)
            result = await session.execute(stmt)
            db_log = result.scalars().first()
            if db_log:
                await session.delete(db_log)
        await session.commit()
        print("Deleted dummy logs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--insert", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--delete", action="store_true")

    args = parser.parse_args()


    async def main():
        if args.insert:
            await insert_logs()
        if args.fetch:
            await fetch_logs()
        if args.update:
            await update_log()
        if args.delete:
            await delete_logs()

    import asyncio
    asyncio.run(main())

