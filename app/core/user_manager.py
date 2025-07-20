import os
import uuid

from dotenv import load_dotenv
from fastapi import Request, Depends
from fastapi_users import IntegerIDMixin, BaseUserManager, FastAPIUsers
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.models.user import User
from app.core.session import get_user_db

load_dotenv()
SECRET = os.getenv("JWT_SECRET")

cookie_transport = CookieTransport(cookie_name="token",
                                   cookie_max_age=3600,
                                   cookie_secure=False)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET,
                       lifetime_seconds=3600,
                       token_audience=["fastapi-users:auth"])


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)