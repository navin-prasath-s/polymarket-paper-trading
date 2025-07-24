import asyncio

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.market import Market, MarketCreate
from app.models.market_change_log import MarketChangeLog, MarketChangeType
from app.models.tracked_market import TrackedMarket
from app.services.clob_service import ClobService
from app.core.session import get_async_manager, engine


class MarketSyncService:

    @staticmethod
    async def get_tracked_markets(db: AsyncSession) -> list[TrackedMarket]:
        result = await db.execute(select(TrackedMarket))
        return result.scalars().all()


    @staticmethod
    async def get_markets(db: AsyncSession) -> list[Market]:
        result = await db.execute(select(Market))
        return result.scalars().all()


    @staticmethod
    async def add_tracked_markets(db: AsyncSession, markets: list) -> list[str]:
        """Add to TrackedMarket and log."""
        added_ids = []
        for market in markets:
            try:
                model_obj = TrackedMarket(**market)
                db.add(model_obj)
                db.add(MarketChangeLog(
                    condition_id=model_obj.condition_id,
                    change_type=MarketChangeType.ADDED
                ))
                await db.commit()
                added_ids.append(model_obj.condition_id)
            except IntegrityError:
                await db.rollback()
                # Ignore if already exists, or you can log/collect error
            except Exception as e:
                await db.rollback()
                print(f"Insert failed for {market['condition_id']}: {e}")
        return added_ids

    @staticmethod
    async def remove_tracked_markets(db: AsyncSession, tracked_markets, removed_ids) -> list[str]:
        """Remove from TrackedMarket and log."""
        removed_ids_list = []
        for m in tracked_markets:
            if m.condition_id in removed_ids:
                try:
                    await db.delete(m)
                    db.add(MarketChangeLog(
                        condition_id=m.condition_id,
                        change_type=MarketChangeType.DELETED
                    ))
                    await db.commit()
                    removed_ids_list.append(m.condition_id)
                except Exception as e:
                    await db.rollback()
                    print(f"Delete failed for {m.condition_id}: {e}")
        return removed_ids_list

    @staticmethod
    async def add_stable_markets(db: AsyncSession, markets: list) -> list[str]:
        """Add new stable markets to Market table."""
        added_ids = []
        for market in markets:
            try:
                # Adjust as needed for your MarketCreate/Market model
                schema_obj = MarketCreate(**market)
                model_obj = Market(**schema_obj.model_dump())
                db.add(model_obj)
                await db.commit()
                added_ids.append(model_obj.condition_id)
            except IntegrityError:
                await db.rollback()
            except Exception as e:
                await db.rollback()
                print(f"Stable market insert failed for {market['condition_id']}: {e}")
        return added_ids


    @staticmethod
    async def mark_markets_untradable(db: AsyncSession, condition_ids: list[str]) -> list[str]:
        """Set is_tradable = False in Market table."""
        updated_ids = []
        result = await db.execute(select(Market).where(Market.condition_id.in_(condition_ids)))
        markets = result.scalars().all()
        for market in markets:
            market.is_tradable = False
            db.add(market)
            updated_ids.append(market.condition_id)
        await db.commit()
        return updated_ids

    @staticmethod
    async def sync_markets(db: AsyncSession) -> dict:
        # 1. Get all live CLOB markets
        clob_markets = ClobService().get_markets()
        clob_condition_ids = {market['condition_id'] for market in clob_markets}

        # 2. Get all current tracked (hot DB) markets
        tracked_markets = await MarketSyncService.get_tracked_markets(db)
        tracked_condition_ids = {m.condition_id for m in tracked_markets}

        # 3. Get all current stable (main) markets
        stable_markets = await MarketSyncService.get_markets(db)
        stable_condition_ids = {m.condition_id for m in stable_markets}

        # 4. Find diffs
        newly_added = clob_condition_ids - tracked_condition_ids
        removed = tracked_condition_ids - clob_condition_ids

        # 5. Add new tracked markets
        to_add = [m for m in clob_markets if m["condition_id"] in newly_added]
        added_tracked = await MarketSyncService.add_tracked_markets(db, to_add)

        # 6. Remove tracked markets
        removed_tracked = await MarketSyncService.remove_tracked_markets(db, tracked_markets, removed)

        # 7. Add to stable market DB (if not present)
        new_for_stable = [m for m in clob_markets if
                          m["condition_id"] in newly_added and m["condition_id"] not in stable_condition_ids]
        added_stable = await MarketSyncService.add_stable_markets(db, new_for_stable)

        # 8. Mark removed as untradable in market DB
        marked_untradable = await MarketSyncService.mark_markets_untradable(db, list(removed))

        return {
            "added_tracked": added_tracked,
            "removed_tracked": removed_tracked,
            "added_stable": added_stable,
            "marked_untradable": marked_untradable
        }



if __name__ == "__main__":
    async def main():
        async with get_async_manager() as db:
            result = await MarketSyncService.sync_markets(db)
            print(result)
        await engine.dispose()
    asyncio.run(main())

# TODO: Make no commits here and make the api route handle the commit/rollback