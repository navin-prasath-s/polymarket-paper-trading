from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payout_log import PayoutLog
from app.models.user_position import UserPosition
from app.models.user_profile import UserProfile


class ResolutionService:

    @staticmethod
    async def resolve_market_winners(db: AsyncSession, winning_markets: list[dict]) -> list[dict]:
        all_results = []

        for winning_market in winning_markets:
            condition_id = winning_market["condition_id"]
            winning_token_ids = set(winning_market["winning_token_ids"])

            positions_stmt = select(UserPosition).where(UserPosition.market == condition_id)
            result = await db.execute(positions_stmt)
            positions = result.scalars().all()

            user_ids = {pos.user_id for pos in positions}
            profiles_stmt = select(UserProfile).where(UserProfile.user_id.in_(user_ids))
            profile_result = await db.execute(profiles_stmt)
            profiles = profile_result.scalars().all()
            user_profiles = {profile.user_id: profile for profile in profiles}

            payout_total = Decimal("0")
            user_payouts = []
            errors = []

            try:
                for position in positions:
                    is_winner = position.token in winning_token_ids

                    payout_log = PayoutLog(
                        user_id=position.user_id,
                        market=condition_id,
                        token=position.token,
                        shares_paid=position.shares if is_winner else Decimal("0"),
                        is_winner=is_winner,
                    )
                    db.add(payout_log)

                    try:
                        if is_winner:
                            user_profile = user_profiles.get(position.user_id)
                            if user_profile:
                                user_profile.balance += position.shares
                                payout_total += position.shares
                                user_payouts.append({
                                    "user_id": position.user_id,
                                    "shares_paid": str(position.shares)
                                })
                    except Exception as user_update_err:
                        errors.append(
                            f"Failed to update balance for user {position.user_id}: {user_update_err}"
                        )

                    # Delete user position for this market regardless
                    try:
                        await db.delete(position)
                    except Exception as del_err:
                        errors.append(
                            f"Failed to delete UserPosition for user {position.user_id}, "
                            f"market {condition_id}, token {position.token}: {del_err}"
                        )

                await db.commit()
            except Exception as e:
                await db.rollback()
                errors.append(f"Critical payout failure for market {condition_id}: {e}")

            all_results.append({
                "market": condition_id,
                "num_payouts": len(user_payouts),
                "payouts": user_payouts,
                "total_paid": str(payout_total),
                "errors": errors,
            })

        return all_results


# TODO: Make no commits here and make the api route handle the commit/rollback