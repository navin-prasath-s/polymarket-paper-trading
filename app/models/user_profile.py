from typing import Annotated
from decimal import Decimal

from sqlmodel import SQLModel, Field
from sqlalchemy import CheckConstraint

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
    balance: Annotated[Decimal, Field(ge=0,
                                      max_digits=10,
                                      decimal_places=2,
                                      nullable=False)] = Decimal("1000.00")

    model_config = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }


class UserProfileCreate(UserProfileBase):
    name: str
    user_name: str


class UserProfileRead(UserProfileBase):
    name: str
    user_name: str
    balance: Decimal



    
