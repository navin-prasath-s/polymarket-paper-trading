from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy import Column
import uuid

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(BINARY(16), primary_key=True)
    )
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
