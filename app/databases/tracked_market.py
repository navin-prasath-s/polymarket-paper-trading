import argparse

from sqlmodel import select

from app.models.tracked_market import TrackedMarket
from app.schemas.tracked_market import TrackedMarketSchema
from app.databases.session import get_session



def create_dummy_data():
    schema_data = [
        TrackedMarketSchema(
            condition_id="cond_001",
            enable_order_book=True,
            accepting_orders=True,
            active=True,
            closed=False,
            archived=False,
            slug="example-market-1"
        ),
        TrackedMarketSchema(
            condition_id="cond_002",
            enable_order_book=False,
            accepting_orders=True,
            active=False,
            closed=True,
            archived=False,
            slug="example-market-2"
        ),
        TrackedMarketSchema(
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



def insert_dummy_data():
    dummy_data = create_dummy_data()
    with get_session() as session:
        session.add_all(dummy_data)
        session.commit()
        print("Dummy data inserted.")


def delete_dummy_data():
    dummy_data = create_dummy_data()
    with get_session() as session:
        for obj in dummy_data:
            db_obj = session.get(TrackedMarket, obj.condition_id)
            if db_obj:
                session.delete(db_obj)
        session.commit()
        print("Dummy data deleted.")


def fetch_first_dummy():
    with get_session() as session:
        statement = select(TrackedMarket)
        result = session.exec(statement).first()
        if result:
            schema_obj = TrackedMarketSchema.model_validate(result)
            print("First DB row as schema:", schema_obj.model_dump_json(indent=2))
        else:
            print("No data found in DB.")

def update_first_dummy():
    with get_session() as session:
        statement = select(TrackedMarket)
        result = session.exec(statement).first()

        if not result:
            print("No records found to update.")
            return

        result.enable_order_book = False
        result.accepting_orders = False

        session.add(result)
        session.commit()
        print("First dummy record updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--insert", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    if args.insert:
        insert_dummy_data()
    if args.delete:
        delete_dummy_data()
    if args.fetch:
        fetch_first_dummy()
    if args.update:
        update_first_dummy()




# python -m app.databases.tracked_market --insert