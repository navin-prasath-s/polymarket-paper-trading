import logging

from fastapi import FastAPI
from app.apis import market, auth, user_profile


logging.basicConfig(level=logging.DEBUG)
app = FastAPI(debug=True)


@app.get("/")
async def root():
    return {"message": "Server is up and running"}

app.include_router(auth.router)

app.include_router(market.router)

app.include_router(user_profile.router)



# uvicorn app.app:app --reload --port 8000