from sqlmodel import SQLModel, Field


class TrackedMarketBase(SQLModel):
    condition_id: str
    enable_order_book: bool
    accepting_orders: bool
    active: bool
    closed: bool
    archived: bool
    market_slug: str

    class Config:
        from_attributes = True


class TrackedMarketCreate(TrackedMarketBase):
    pass



class TrackedMarket(TrackedMarketBase, table=True):
    __tablename__ = "tracked_markets"

    condition_id: str = Field(primary_key=True)

