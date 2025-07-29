import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_position import UserPosition
from app.models.user_profile import UserProfile


class ResolutionService:

    @staticmethod
    async def resolve_market_winners(db: AsyncSession, winning_market: dict) -> dict:
        condition_id = winning_market["condition_id"]
        winning_token_ids = set(winning_market["winning_token_ids"])

        positions_stmt = select(UserPosition).where(UserPosition.market == condition_id)
        result = await db.execute(positions_stmt)
        positions = result.scalars().all()

        payout_total = Decimal("0")
        user_payouts = []

        for position in positions:
            if position.token in winning_token_ids:
                user_profile_stmt = select(UserProfile).where(UserProfile.user_id == position.user_id)
                user_profile_result = await db.execute(user_profile_stmt)
                user_profile = user_profile_result.scalar_one_or_none()

                if user_profile:
                    user_profile.balance += position.shares
                    payout_total += position.shares
                    user_payouts.append({
                        "user_id": position.user_id,
                        "shares_paid": str(position.shares)
                    })

            await db.delete(position)

        await db.commit()

        return {
            "market": condition_id,
            "num_payouts": len(user_payouts),
            "payouts": user_payouts,
            "total_paid": str(payout_total),
        }
