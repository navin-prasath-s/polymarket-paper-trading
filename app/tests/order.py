from decimal import Decimal
import asyncio
from unittest.mock import patch, Mock

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.order import create_buy_order, create_sell_order
from app.core.session import engine, async_session_maker
from app.models.order_fill import OrderFill
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.user_position import UserPosition
from app.models.market import Market
from app.models.market_outcome import MarketOutcome
from app.models.order import OrderBuyCreate, Order, OrderType, OrderSide, OrderStatus, OrderSellCreate


async def setup_data(db: AsyncSession):
    user = User(
        email="user10@test.com",
        hashed_password="user10@test.pass",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    db.add(user)
    await db.flush()

    user_profile = UserProfile(
        user_id=user.id,
        name="user10",
        user_name="user10user",
        balance=Decimal("1000.00")
    )
    db.add(user_profile)
    await db.flush()

    market = Market(
        condition_id="condition1",
        market_slug="market1",
        is_tradable=True
    )
    db.add(market)
    await db.flush()

    market1_outcome1 = MarketOutcome(
        market="condition1",
        token="token1",
        outcome_text="Outcome 1"
    )
    market1_outcome2 = MarketOutcome(
        market="condition1",
        token="token2",
        outcome_text="Outcome 2"
    )
    db.add(market1_outcome1)
    db.add(market1_outcome2)
    await db.flush()

    await db.commit()
    await db.refresh(market1_outcome1)
    return {
        "user_id": user.id,
        "user_profile_id": user_profile.user_id,
        "market_condition_id": market.condition_id,
        "market1_token1": market1_outcome1.token,
        "market1_token2": market1_outcome2.token,
    }




async def test_create_market_buy_order_new_share_success():
    async with async_session_maker() as db:
        ids = await setup_data(db)
        await db.commit()


    async with async_session_maker() as db:
        user = await db.get(User, ids["user_id"])
        user_profile = await db.get(UserProfile, ids["user_profile_id"])
        initial_balance = user_profile.balance

        order = OrderBuyCreate(
            market="condition1",
            token="token1",
            order_type=OrderType.MARKET,
            amount_usdc=Decimal("200.00"),
        )


        with patch("app.apis.order.ClobService") as mock_clob_service:
            with patch("app.apis.order.OrderService") as mock_order_service:

                mock_clob_service.get_book_by_token_id.return_value = Mock()

                mock_order_service.return_value.simulate_buy_transaction.return_value = {
                    'status': 'filled',
                    'shares_filled': Decimal("1750.00"),
                    'total_cost': Decimal("200.00"),
                    'fills': [
                        {'fill_price': Decimal("0.1"), 'fill_shares': Decimal("1500.0")},
                        {'fill_price': Decimal("0.2"), 'fill_shares': Decimal("250.0")},
                    ]
                }

                result = await create_buy_order(order, db, user)
        print(result)


        assert result["status"] == "success"
        assert "order_id" in result
        assert result["details"]["amount_usdc"] == Decimal("200.00")
        assert result["details"]["shares"] == Decimal("1750.00")
        assert result["details"]["average_price"] == Decimal("200.00") / Decimal("1750.00")
        assert result["details"]["fills"] == 2

        await db.refresh(user_profile)
        assert user_profile.balance == initial_balance - Decimal("200.00")
        assert user_profile.balance == Decimal("800.00")

        position = await db.scalar(
            select(UserPosition).where(
                UserPosition.user_id == user.id,
                UserPosition.market == "condition1",
                UserPosition.token == "token1"
            )
        )
        assert position is not None
        assert position.shares == Decimal("1750.00")

        order_record = await db.scalar(
            select(Order).where(
                Order.user_id == user.id,
                Order.market == "condition1",
                Order.token == "token1"
            )
        )

        assert order_record is not None
        assert order_record.side == OrderSide.BUY
        assert order_record.order_type == OrderType.MARKET
        assert order_record.status == OrderStatus.FILLED
        assert order_record.amount_usdc == Decimal("200.00")
        assert order_record.shares == Decimal("1750.00")

        fills = await db.scalars(
            select(OrderFill).where(OrderFill.order_id == order_record.order_id)
        )
        fill_list = list(fills)
        assert len(fill_list) == 2

        await db.close()


async def test_create_market_sell_order_partial_success():
    async with async_session_maker() as db:
        # Setup: get user, profile, and confirm balance and shares as in your buy test
        user = await db.scalar(select(User).where(User.email == "user10@test.com"))
        user_profile = await db.get(UserProfile, user.id)
        position = await db.scalar(
            select(UserPosition).where(
                UserPosition.user_id == user.id,
                UserPosition.market == "condition1",
                UserPosition.token == "token1"
            )
        )
        initial_balance = user_profile.balance  # Should be 800.00 after buy
        initial_shares = position.shares       # Should be 1750.00 after buy

        # We sell 750 shares at custom fill prices
        sell_shares = Decimal("750.00")
        sell_order = OrderSellCreate(
            market="condition1",
            token="token1",
            order_type=OrderType.MARKET,
            shares=sell_shares
        )

        # You decide fill prices and shares so that total_proceeds = 500*0.15 + 250*0.2 = 75 + 50 = 125.00
        fills = [
            {'fill_price': Decimal("0.15"), 'fill_shares': Decimal("500.0")},
            {'fill_price': Decimal("0.2"),  'fill_shares': Decimal("250.0")},
        ]
        total_proceeds = (Decimal("500.0") * Decimal("0.15")) + (Decimal("250.0") * Decimal("0.2"))  # 75 + 50 = 125

        with patch("app.apis.order.OrderService.simulate_sell_transaction") as mock_sim:
            mock_sim.return_value = {
                'status': 'filled',
                'shares_sold': sell_shares,
                'total_proceeds': total_proceeds,
                'fills': fills
            }

            # Actually call your endpoint logic
            result = await create_sell_order(sell_order, db, user)
            print(result)

        # Assertions: balance, shares, order in db, fills, etc.
        await db.refresh(user_profile)
        await db.refresh(position)

        assert result["status"] == "success"
        assert "order_id" in result
        assert result["details"]["amount_usdc"] == total_proceeds
        assert result["details"]["shares"] == sell_shares
        assert result["details"]["average_price"] == total_proceeds / sell_shares
        assert result["details"]["fills"] == 2

        # After selling, balance should be +125 (so 800 + 125 = 925)
        assert user_profile.balance == initial_balance + total_proceeds
        # After selling, shares should be 1750 - 750 = 1000
        assert position.shares == initial_shares - sell_shares

        # Check order and fills
        order_record = await db.scalar(
            select(Order).where(
                Order.user_id == user.id,
                Order.market == "condition1",
                Order.token == "token1",
                Order.side == OrderSide.SELL
            )
        )
        assert order_record is not None
        assert order_record.side == OrderSide.SELL
        assert order_record.order_type == OrderType.MARKET
        assert order_record.status == OrderStatus.FILLED
        assert order_record.amount_usdc == total_proceeds
        assert order_record.shares == sell_shares

        fill_objs = await db.scalars(
            select(OrderFill).where(OrderFill.order_id == order_record.order_id)
        )
        fill_list = list(fill_objs)
        assert len(fill_list) == 2
        assert fill_list[0].fill_price == Decimal("0.15")
        assert fill_list[0].fill_shares == Decimal("500.0")
        assert fill_list[1].fill_price == Decimal("0.2")
        assert fill_list[1].fill_shares == Decimal("250.0")

        await db.close()

if __name__ == "__main__":
    async def main():
        await test_create_market_buy_order_new_share_success()
        await test_create_market_sell_order_partial_success()
        await engine.dispose()
    asyncio.run(main())