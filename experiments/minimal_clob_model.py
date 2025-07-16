from __future__ import annotations

from pydantic import BaseModel


class Token(BaseModel):
    token_id: str
    outcome: str
    price: float
    winner: bool

class MinimalClobModel(BaseModel):
    condition_id: str
    market_slug: str
    question: str
    enable_order_book: bool
    active: bool
    closed: bool
    archived: bool
    accepting_orders: bool
    tokens: list[Token]

    model_config = {
        "extra": "ignore"
    }

