from sqlmodel import SQLModel

class Market(SQLModel):
    condition_id: str
    market_slug: str
    is_tradable: bool

    class Config:
        from_attributes = True