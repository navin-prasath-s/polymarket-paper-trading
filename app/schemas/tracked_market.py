from pydantic import BaseModel

class TrackedMarketSchema(BaseModel):
    condition_id: str
    enable_order_book: bool
    accepting_orders: bool
    active: bool
    closed: bool
    archived: bool
    market_slug: str

    class Config:
        from_attributes = True