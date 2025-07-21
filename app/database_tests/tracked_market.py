import argparse

from sqlalchemy.future import select

from app.models.tracked_market import TrackedMarket, TrackedMarketCreate
from app.core.session import get_async_session



def create_dummy_data():
    schema_data = [
        TrackedMarketCreate(
            condition_id="cond_001",
            enable_order_book=True,
            accepting_orders=True,
            active=True,
            closed=False,
            archived=False,
            slug="example-market-1"
        ),
        TrackedMarketCreate(
            condition_id="cond_002",
            enable_order_book=False,
            accepting_orders=True,
            active=False,
            closed=True,
            archived=False,
            slug="example-market-2"
        ),
        TrackedMarketCreate(
            condition_id="cond_003",
            enable_order_book=True,
            accepting_orders=False,
            active=False,
            closed=True,
            archived=True,
            slug="example-market-3"
        ),
    ]

    orm_models = [TrackedMarket(**schema.dict()) for schema in schema_data]
    return orm_models



async def insert_dummy_data():
    dummy_data = create_dummy_data()
    async with get_async_session() as session:
        session.add_all(dummy_data)
        await session.commit()
        print("Dummy data inserted.")


async def delete_dummy_data():
    dummy_data = create_dummy_data()
    async with get_async_session() as session:
        for obj in dummy_data:
            db_obj = await session.get(TrackedMarket, obj.condition_id)
            if db_obj:
                await session.delete(db_obj)
        await session.commit()
        print("Dummy data deleted.")


async def fetch_first_dummy():
    async with get_async_session() as session:
        statement = select(TrackedMarket)
        result = (await session.execute(statement)).scalars().first()
        if result:
            schema_obj = TrackedMarketCreate.model_validate(result)
            print("First DB row as schema:", schema_obj.model_dump_json(indent=2))
        else:
            print("No data found in DB.")

async def update_first_dummy():
    async with get_async_session() as session:
        statement = select(TrackedMarket)
        result = (await session.execute(statement)).scalars().first()

        if not result:
            print("No records found to update.")
            return

        result.enable_order_book = False
        result.accepting_orders = False

        session.add(result)
        await session.commit()
        print("First dummy record updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--insert", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()


    async def main():
        if args.insert:
            await insert_dummy_data()
        if args.delete:
            await delete_dummy_data()
        if args.fetch:
            await fetch_first_dummy()
        if args.update:
            await update_first_dummy()




# python -m app.database_tests.tracked_market --insert