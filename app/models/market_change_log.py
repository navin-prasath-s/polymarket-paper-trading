from datetime import datetime, timezone
from enum import Enum

from sqlmodel import SQLModel, Field

class MarketChangeType(str, Enum):
    ADDED = "added"
    DELETED = "deleted"

class MarketChangeLog(SQLModel, table=True):
    __tablename__ = "market_change_logs"

    id: int = Field(primary_key=True)
    condition_id: str
    change_type: MarketChangeType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))