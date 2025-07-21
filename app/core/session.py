from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import Session
from dotenv import load_dotenv

from app.models.user import User
load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

url = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_async_engine(url, echo=True)
async_session_maker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


# def get_sync_session():
#     return Session(engine)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@asynccontextmanager
async def get_async_manager() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)