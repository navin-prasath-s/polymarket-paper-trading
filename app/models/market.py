from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.market_outcome import MarketOutcome


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

    outcomes: list["MarketOutcome"] | None = Relationship(back_populates="market_obj")


# TODO: Add unique constraint on condition_id