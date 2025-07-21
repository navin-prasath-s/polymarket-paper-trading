import logging

from fastapi import FastAPI
from app.apis import auth, market_events, markets, auth


logging.basicConfig(level=logging.DEBUG)
app = FastAPI(debug=True)


@app.get("/")
async def root():
    return {"message": "Hello"}

app.include_router(auth.router)
app.include_router(market_events.router)
app.include_router(markets.router)



# uvicorn app.app:app --reload --port 8000