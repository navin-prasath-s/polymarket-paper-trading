from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile


class UserProfileService:
    @staticmethod
    async def amount_change_balance(
            delta: Decimal,
            user_id: int,
            db: AsyncSession
    ) -> UserProfile:
        if not isinstance(delta, Decimal):
            raise TypeError("Delta must be a Decimal instance.")

        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile: UserProfile = result.scalar_one()

        if not profile:
            raise ValueError("UserProfile not found for the given user_id.")

        if profile.balance + delta < 0:
            raise ValueError("Insufficient funds: balance cannot go negative.")

        profile.balance += delta
        await db.flush()
        return profile


