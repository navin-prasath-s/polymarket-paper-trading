from typing import Optional, Annotated
from decimal import Decimal

from fastapi_users import schemas
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, CheckConstraint

from sqlmodel import SQLModel, Field, Relationship


class UserProfileBase(SQLModel):
    pass

    class Config:
        from_attributes = True

class UserProfile(UserProfileBase,table=True):
    __tablename__ = "user_profiles"

    __table_args__ = (
        CheckConstraint("balance >= 0", name="balance_non_negative"),
    )

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    name: str = Field(nullable=False)
    user_name: str = Field(unique=True, nullable=False)
    # balance: Annotated[float, Field(default=1000.0, nullable=False)]
    balance: Annotated[Decimal, Field(ge=0,
                                      max_digits=10,
                                      decimal_places=2,
                                      nullable=False)] = Decimal("1000.00")

    user: "User" = Relationship(back_populates="user_profile")

    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }


class UserProfileCreate(UserProfileBase):
    name: str
    user_name: str





class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_profile: Optional[UserProfile] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )



class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass








