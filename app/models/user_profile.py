from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field, Relationship

from app.models.user import User


class UserProfileBase(SQLModel):
    pass

    class Config:
        from_attributes = True


class UserProfile(UserProfileBase,table=True):
    __tablename__ = "user_profiles"

    user_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    name: str = Field(nullable=False)
    user_name: str = Field(unique=True, nullable=False)
    balance: float = Field(default=1000.0, nullable=False)

    user: "User" = Relationship(
        back_populates="profile",
        sa_relationship_kwargs={"uselist": False},
    )