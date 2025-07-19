from fastapi import FastAPI
from app.apis.market_events import router as market_router

app = FastAPI()
app.include_router(market_router)

# uvicorn app.main:app --reload --port 8000