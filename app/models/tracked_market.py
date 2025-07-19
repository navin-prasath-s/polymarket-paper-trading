from sqlmodel import SQLModel, Field

class TrackedMarket(SQLModel, table=True):
    __tablename__ = "tracked_markets"

    condition_id: str = Field(primary_key=True)
    enable_order_book: bool
    accepting_orders: bool
    active: bool
    closed: bool
    archived: bool
    slug: str