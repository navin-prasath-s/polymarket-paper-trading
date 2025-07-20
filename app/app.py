import logging

from fastapi import FastAPI, Cookie
# from app.apis import market_events, markets, auth
from app.apis import auth


logging.basicConfig(level=logging.DEBUG)
app = FastAPI(debug=True)


@app.get("/")
async def root():
    return {"message": "Hello"}

app.include_router(auth.router)

# @app.get("/debug-validate")
# def debug_validate(token: str | None = Cookie(default=None)):
#     import jwt, os
#     payload = None
#     try:
#         print(f"Decoding token: {token}")
#         payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
#     except Exception as e:
#         return {"error": str(e)}
#     return {"payload": payload}

# app.include_router(market_events.router)
# app.include_router(markets.router)



# uvicorn app.app:app --reload --port 8000