from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.market import Market


class MarketOutcomeBase(SQLModel):
    class Config:
        from_attributes = True

class MarketOutcome(MarketOutcomeBase, table=True):
    __tablename__ = "market_outcomes"

    market: str = Field(foreign_key="markets.condition_id",
                        primary_key=True)

    token: str = Field(primary_key=True,
                       nullable=False)

    outcome_text: str = Field(default=None,
                              nullable=True)

    is_winner: bool = Field(default=False,
                            nullable=False)

    market_obj: Optional["Market"] = Relationship(back_populates="outcomes")