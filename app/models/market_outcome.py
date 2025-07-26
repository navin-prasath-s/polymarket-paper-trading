from sqlmodel import SQLModel, Field

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

