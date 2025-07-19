from sqlmodel import SQLModel, Field

class Market(SQLModel, table=True):
    __tablename__ = "markets"

    condition_id: str = Field(primary_key=True)
    market_slug: str
    is_tradable: bool