from sqlmodel import Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(url, echo=True)

def get_session():
    return Session(engine)