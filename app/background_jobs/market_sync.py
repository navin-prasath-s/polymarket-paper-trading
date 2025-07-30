import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_async_manager, engine
from app.services.market_sync_service import MarketSyncService
from app.services.resolution_service import ResolutionService

async def sync_market_and_resolve(db: AsyncSession):
    result = await MarketSyncService.sync_markets(db)
    resolved_markets = result.get("winners", [])
    if resolved_markets:
        resolution_info  = await ResolutionService.resolve_market_winners(db, resolved_markets)
    else:
        resolution_info = {}

    combined_result = {
        **result,
        "resolution_info": resolution_info,
    }

    return combined_result

async def run_periodic_sync():
    while True:
        async with get_async_manager() as db:
            result = await sync_market_and_resolve(db)
        with open("sync_and_resolve_dump.txt", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print("Sync complete, sleeping for 5 minutes")
        await engine.dispose()
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_periodic_sync())