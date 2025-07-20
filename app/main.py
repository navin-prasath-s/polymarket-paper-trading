from fastapi import FastAPI
# from app.apis.market_events import router as market_router
from app.apis import market_events, markets

app = FastAPI()
app.include_router(market_events.router)
app.include_router(markets.router)
# uvicorn app.main:app --reload --port 8000