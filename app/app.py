from fastapi import FastAPI
from app.apis import market_events, markets
from app.core.user_manager import fastapi_users, auth_backend
from app.schemas.user import UserRead, UserCreate, UserUpdate

app = FastAPI()
app.include_router(market_events.router)
app.include_router(markets.router)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)












# uvicorn app.main:app --reload --port 8000