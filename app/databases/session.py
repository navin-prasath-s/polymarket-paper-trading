from typing import Generator
import os

from sqlmodel import Session, create_engine
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(url, echo=True)


def get_sync_session():
    return Session(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session