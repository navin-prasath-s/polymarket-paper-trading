from datetime import datetime, timezone

from sqlmodel import SQLModel, Field

class MarketChangeLog(SQLModel, table=True):
    __tablename__ = "market_change_logs"

    id: int = Field(primary_key=True)
    condition_id: str
    change_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))