from fastapi import FastAPI
from app.apis import market_events, markets

app = FastAPI()
app.include_router(market_events.router)
app.include_router(markets.router)
# uvicorn app.main:app --reload --port 8000