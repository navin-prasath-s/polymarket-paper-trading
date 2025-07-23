from sqlmodel import SQLModel, Field


class MarketBase(SQLModel):
    condition_id: str
    market_slug: str

    class Config:
        from_attributes = True


class MarketRead(MarketBase):
    pass

class MarketCreate(MarketBase):
    pass

class Market(MarketBase, table=True):
    __tablename__ = "markets"

    condition_id: str = Field(primary_key=True)
    market_slug: str = Field(nullable=False)
    is_tradable: bool = Field(default=True, nullable=False)


# TODO: Add unique constraint on condition_id